
#!/usr/local/bin/python
#
# (c) Copyright 2013, 2014, University of Manchester
#
# HydraPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HydraPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HydraPlatform.  If not, see <http://www.gnu.org/licenses/>
#

__version__ = '0.1.3'

import bcrypt
password = ''
bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())


import sys

import six


import logging
log = logging.getLogger(__name__)

try:
    import spyne
    main_version = spyne.__version__.split('.')[0]
    sub_version = spyne.__version__.split('.')[1]

    if six.PY3 and int(sub_version) < 13:
        log.warn("\nThe current version of spyne on PYPI does not work well with Python 3. Please run the following command to get the latest development version, which does.\n\n"+
                        "pip install --upgrade git+https://github.com/arskom/spyne.git@spyne-2.13.2-alpha#egg=spyne\n\n")
        sys.exit()

except ModuleNotFoundError as e:
        log.warn("\nOne of the dependencies -- Spyne -- is not installed."+
                        " The current version of spyne on PYPI does not work well with Python 3. Please run the following command to get the latest development version, which does.\n\n"+
                        "pip install git+https://github.com/arskom/spyne.git@spyne-2.13.2-alpha#egg=spyne\n\n")
        sys.exit()



import spyne.service #Needed for build script.


from decimal import getcontext
getcontext().prec = 26

from spyne.application import Application
from spyne.protocol.soap import Soap11
from spyne.protocol.json import JsonDocument, JsonP
from spyne.protocol.http import HttpRpc
from spyne.server.null import NullServer

import spyne.decorator

from spyne.error import Fault, ArgumentError

import hydra_base as hb
from hydra_base.exceptions import HydraError
from hydra_base.util import hdb


from hydra_server.server.network import NetworkService
from hydra_server.server.project import ProjectService
from hydra_server.server.attributes import AttributeService, AttributeGroupService
from hydra_server.server.scenario import ScenarioService
from hydra_server.server.data import DataService
from hydra_server.server.users import UserService
from hydra_server.server.template import TemplateService
from hydra_server.server.static import ImageService, FileService
from hydra_server.server.groups import ResourceGroupService
from hydra_server.server.units import UnitService
from hydra_server.server.rules import RuleService
from hydra_server.server.notes import NoteService
from hydra_server.server.service import AuthenticationService,\
    LogoutService,\
    AuthenticationError,\
    ObjectNotFoundError,\
    HydraServiceError,\
    HydraDocument
from hydra_server.server.sharing import SharingService
from spyne.util.wsgi_wrapper import WsgiMounter
import socket

from beaker.middleware import SessionMiddleware

applications = [
    AuthenticationService,
    UserService,
    LogoutService,
    NetworkService,
    ProjectService,
    ResourceGroupService,
    AttributeService,
    AttributeGroupService,
    ScenarioService,
    DataService,
    TemplateService,
    ImageService,
    FileService,
    SharingService,
    UnitService,
    RuleService,
    NoteService,
]



import datetime
import traceback

from cheroot.wsgi import Server
from hydra_base.db import commit_transaction, rollback_transaction, close_session


def _on_method_call(ctx):

    #don't do anythying if we're in test mode:
    if ctx.transport.app.transport == NullServer.transport:
        return

    #otherwise it must have a 'req_env' as it's a wsgi application
    env = ctx.transport.req_env

    if ctx.function == AuthenticationService.login or ctx.function == AuthenticationService.get_remote_session:
        return

    if ctx.in_object is None:
        raise ArgumentError("RequestHeader is null")

    if ctx.in_header is None:
        raise AuthenticationError("No headers!")

    session = env.get('beaker.session', {})

    if session.get('user_id') is None:

        raise Fault("No Session!")

    ctx.in_header.user_id = session['user_id']
    ctx.in_header.username = session['username']


def _on_method_context_closed(ctx):
    log.info("Committing...")
    commit_transaction()

    log.info("Closing session")
    close_session()

class HydraSoapApplication(Application):
    """
        Subclass of the base spyne Application class.

        Used to handle transactions in request handlers and to log
        how long each request takes.

        Used also to handle exceptions, allowing server side exceptions
        to be send to the client.
    """
    def __init__(self, services, tns, name=None,
                 in_protocol=None, out_protocol=None):

        Application.__init__(self, services, tns, name, in_protocol, out_protocol)

        self.event_manager.add_listener('method_call', _on_method_call)
        self.event_manager.add_listener("method_context_closed",
                                        _on_method_context_closed)

    def call_wrapper(self, ctx):
        try:

            log.info("Received request: %s", ctx.function)

            start = datetime.datetime.now()
            res =  ctx.service_class.call_wrapper(ctx)
            log.info("Call took: %s"%(datetime.datetime.now()-start))
            return res
        except ObjectNotFoundError as e:
            log.critical(e)
            rollback_transaction()
            raise
        except HydraError as e:
            log.critical(e)
            rollback_transaction()
            traceback.print_exc(file=sys.stdout)
            code = "HydraError %s"%e.code
            raise HydraServiceError(e.message, code)
        except Fault as e:
            log.critical(e)
            rollback_transaction()
            raise
        except Exception as e:
            log.critical(e)
            traceback.print_exc(file=sys.stdout)
            rollback_transaction()
            raise Fault('Server', e)

class HydraServer():

    def __init__(self, db_uri):

        hb.connect(db_uri)

        #hdb.create_default_users_and_perms()
        #hdb.create_default_units_and_dimensions()
        #hdb.make_root_user()
        #hdb.create_default_net()

        #commit_transaction()

        self.soap_application = None
        self.json_application = None
        self.jsonp_application = None
        self.http_application = None

    def create_soap_application(self):

        app = HydraSoapApplication(applications, tns='hydra.base',
                                   in_protocol=Soap11(validator='lxml'),
                                   out_protocol=Soap11()
                                  )
        self.soap_application = app;

    def create_json_application(self):

        app = HydraSoapApplication(applications, tns='hydra.base',
                                   in_protocol=HydraDocument(validator='soft'),
                                   out_protocol=JsonDocument()
                                  )
        self.json_application = app;

    def create_jsonp_application(self):

        app = HydraSoapApplication(applications, tns='hydra.base',
                                   in_protocol=HttpRpc(validator='soft'),
                                   out_protocol=JsonP("hydra_cb")
                                  )
        self.jsonp_application = app;

    def create_http_application(self):

        app = HydraSoapApplication(applications, tns='hydra.base',
                                   in_protocol=HttpRpc(validator='soft'),
                                   out_protocol=JsonDocument()
                                  )
        self.http_application = app;

    def run_server(self, port=None, db_uri=None):

        log.info("home_dir %s", hb.config.get('DEFAULT', 'home_dir'))
        log.info("hydra_base_dir %s", hb.config.get('DEFAULT', 'hydra_base_dir'))
        log.info("common_app_data_folder %s", hb.config.get('DEFAULT', 'common_app_data_folder'))
        log.info("win_common_documents %s", hb.config.get('DEFAULT', 'win_common_documents'))
        log.info("sqlite url %s", hb.config.get('mysqld', 'url'))
        log.info("layout_xsd_path %s", hb.config.get('hydra_server', 'layout_xsd_path'))
        log.info("default_directory %s", hb.config.get('plugin', 'default_directory'))
        log.info("result_file %s", hb.config.get('plugin', 'result_file'))
        log.info("plugin_xsd_path %s", hb.config.get('plugin', 'plugin_xsd_path'))
        log.info("log_config_path %s", hb.config.get('logging_conf', 'log_config_path'))

        if port is None:
            port = hb.config.getint('hydra_server', 'port', 8080)

        domain = hb.config.get('hydra_server', 'domain', '127.0.0.1')

        check_port_available(domain, port)

        default_ns = 'soap_server.hydra_complexmodels'

        if six.PY3:
            spyne.const.xml.DEFAULT_NS = default_ns
        else:
            spyne.const.xml_ns.DEFAULT_NS = default_ns

        cp_wsgi_application = Server((domain, port), application, numthreads=10)

        log.info("listening to http://%s:%s", domain, port)
        log.info("wsdl is at: http://%s:%s/soap/?wsdl", domain, port)

        try:
            cp_wsgi_application.start()
        except KeyboardInterrupt:
            cp_wsgi_application.stop()

def check_port_available(domain, port):
    """
        Given a domain and port, check to see whether that combination is available
        for hydra to use.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((domain, port))

    if result == 0:
        raise HydraError("Something else is already running on port %s"%port)

    log.info("Port %s is available", port)

application = None

def initialize(db_uri):
    global application
    global api_server
    api_server = initialize_api_server(db_uri)
    wsgi_app = initialise_wsgi_application(api_server)
    application = wsgi_app
    return application, api_server

def initialize_api_server(db_uri, test=False):
    api_server = HydraServer(db_uri)
    #only create the JSON one when in test mode
    api_server.create_json_application()

    if test is False:
        api_server.create_soap_application()
        api_server.create_jsonp_application()
        api_server.create_http_application()

    return api_server

def initialise_wsgi_application(api_server):

    wsgi_application = WsgiMounter({
        hb.config.get('hydra_server', 'soap_path', 'soap'): api_server.soap_application,
        hb.config.get('hydra_server', 'json_path', 'json'): api_server.json_application,
        'jsonp': api_server.jsonp_application,
        hb.config.get('hydra_server', 'http_path', 'http'): api_server.http_application,
    })

    for server in wsgi_application.mounts.values():
        server.max_content_length = 200 * 0x100000 # 200 MB
        server.block_length = 10*0x10000 # 65KB

    # Configure the SessionMiddleware
    session_opts = {
        'session.type': 'file' if hb.db.hydra_db_url.startswith('sqlite') else 'ext:database',
        'session.cookie_expires': True,
        'session.data_dir':'/tmp',
        'session.file_dir':'/tmp/auth',
        'session.url': hb.db.hydra_db_url,
        'session.sa_opts': {'sa.pool_pre_ping': True}
    }
    app = SessionMiddleware(wsgi_application, session_opts)

    return app
