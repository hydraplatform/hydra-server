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
import requests
import logging
import json
from spyne.model.primitive import Mandatory, String, Unicode, Integer
from spyne.error import Fault
from spyne.model.complex import ComplexModel
from spyne.decorator import rpc
from .complexmodels import LoginResponse
import hydra_base as hb
from hydra_base import config
from hydra_base.exceptions import HydraError
from spyne.protocol.json import JsonDocument

from spyne.service import ServiceBase

log = logging.getLogger(__name__)

class HydraDocument(JsonDocument):
    """An implementation of the json protocol
       with request headers working"""

    def create_in_document(self, ctx, in_string_encoding=None):
        super(HydraDocument, self).create_in_document(ctx, in_string_encoding)

    def decompose_incoming_envelope(self, ctx, message=JsonDocument.REQUEST):
        super(HydraDocument, self).decompose_incoming_envelope(ctx, message)
        req = ctx.transport.req

        ctx.in_header_doc = {}
        for r in req:
            if r.find('HTTP') == 0:
                key = r[5:].lower()
                val = [req[r].lower()]
                ctx.in_header_doc[key] = val

    def deserialize(self, ctx, message):
        super(HydraDocument, self).deserialize(ctx, message)
        if ctx.descriptor.in_header:
            in_header_class = ctx.descriptor.in_header[0]
            ctx.in_header = in_header_class()
            for k, v in ctx.in_header_doc.items():
                setattr(ctx.in_header, k, v[0])

class RequestHeader(ComplexModel):
    __namespace__ = 'hydra.base'

    username = Unicode
    user_id = Unicode
    appname = Unicode

    def __init__(self):
        self.appname = None
        self.user_id = None
        self.username = None

class HydraService(ServiceBase):
    __tns__ = 'hydra.base'
    __in_header__ = RequestHeader

class AuthenticationError(Fault, HydraError):
    __namespace__ = 'hydra.base'

    def __init__(self, user_name):
        Fault.__init__(self,
                       faultcode='Client.AuthenticationError',
                       faultstring='Invalid authentication request for %r' % user_name
                      )
        HydraError.__init__(self, 'Invalid authentication request for %r' % user_name)

class AuthorizationError(Fault, HydraError):
    __namespace__ = 'hydra.authentication'

    def __init__(self, code="AuthorizationError"):

        Fault.__init__(self,
                       faultcode='Client.AuthorizationError',
                       faultstring='You are not authozied to access this resource.'
                      )

class HydraServiceError(Fault, HydraError):
    __namespace__ = 'hydra.error'

    def __init__(self, message, code="HydraError"):

        Fault.__init__(self,
                       faultcode=code,
                       faultstring=message
                      )

class ObjectNotFoundError(HydraServiceError):
    __namespace__ = 'hydra.error'

    def __init__(self, message):

        Fault.__init__(self,
                       faultcode='NoObjectFoundError',
                       faultstring=message
                      )

class LogoutService(HydraService):
    __tns__ = 'hydra.authentication'

    @rpc(Unicode, _returns=String, _throws=AuthenticationError)
    def logout(ctx, session_id):
        """
            Log a user out by deleting their session. The session ID parameter is
            only used for validation here, and exists mainly to match the hydra base
            argument structure, to make unit testing easier.
        """

        #If we're in test mode, ignore
        #don't do anythying if we're in test mode:
        if ctx.transport.app.transport == 'noconn://null.spyne':
            return 'OK'

        if session_id is not None and ctx.transport.req_env['beaker.session'].id != session_id:
            #ignore
            return 'OK'

        ctx.transport.req_env['beaker.session'].delete()

        return "OK"

class AuthenticationService(ServiceBase):
    __tns__ = 'hydra.base'

    @rpc(Mandatory.Unicode, Unicode, _returns=LoginResponse, _throws=AuthenticationError)
    def login(ctx, username, password):
        try:
            if username is None:
                raise HydraError("No Username specified.")
            if isinstance(username, bytes):
                username = username.encode('utf-8')

            if password is None:
                raise HydraError("No password specified")
            if isinstance(password, bytes):
                password = password.encode('utf-8')
            log.debug("%s, %s",username, password)
            user_id = hb.hdb.login_user(username, password)
        except HydraError as e:
            raise AuthenticationError(e)

        if hasattr(ctx.transport, 'req_env'):
            ctx.transport.req_env['beaker.session']['user_id'] = user_id
            ctx.transport.req_env['beaker.session']['username'] = username
            ctx.transport.req_env['beaker.session'].save()

        login_response = LoginResponse()
        login_response.user_id = user_id
        login_response.username = username

        log.info(ctx.transport.req_env['beaker.session'])

        return login_response

    @rpc(Unicode, _returns=LoginResponse)
    def get_remote_session(ctx, session_id=None):
        """
            This function takes a session id which was not generated by this server,
            but by another hydra server. It makes a request to the remote server using
            the endpoint 'get_hydra_session', which returns the user ID, username and session ID.
            From here we can set the session ID as though it was generated here.

        """
        session_data = hb.get_session_user(session_id)

        if session_data is None:
            return None

        ctx.transport.req_env['beaker.session']['user_id'] = session_data['user_id']
        ctx.transport.req_env['beaker.session']['username'] = session_data['username']
        ctx.transport.req_env['beaker.session']['id'] = session_id
        ctx.transport.req_env['beaker.session'].save()

        login_response = LoginResponse()
        login_response.user_id = session_data.get('user_id')
        login_response.username = session_data.get('username')
        return login_response
