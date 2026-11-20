"""
    End-to-end check through the real spyne request pipeline that undeclared
    request headers never reach the service function.

    Needs spyne (and hydra_base) importable, so is skipped otherwise.
"""
import io
import json

import pytest

pytest.importorskip("spyne")
pytest.importorskip("hydra_base")

from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.primitive import Unicode
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication

from hydra_server.server.service import HydraDocument, HydraService


class EchoService(HydraService):
    @rpc(_returns=Unicode)
    def echo_header(ctx):
        return json.dumps(sorted(vars(ctx.in_header)))


def _call(extra_headers):
    app = Application([EchoService], tns='hydra.base',
                      in_protocol=HydraDocument(validator='soft'),
                      out_protocol=JsonDocument())
    body = b'{"echo_header": {}}'
    environ = {
        'REQUEST_METHOD': 'POST', 'PATH_INFO': '/', 'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80', 'wsgi.url_scheme': 'http', 'wsgi.input': io.BytesIO(body),
        'CONTENT_LENGTH': str(len(body)), 'CONTENT_TYPE': 'application/json',
        'wsgi.errors': io.StringIO(), 'wsgi.version': (1, 0), 'wsgi.multithread': False,
        'wsgi.multiprocess': False, 'wsgi.run_once': False,
    }
    environ.update(extra_headers)
    out = b''.join(WsgiApplication(app)(environ, lambda status, headers: None))
    return json.loads(out)


def test_only_declared_header_fields_reach_the_service():
    result = _call({'HTTP_APPNAME': 'x', 'HTTP_FILTER_TYPE': 'id',
                    'HTTP_FILTER_VALUE': '__import__("os").getcwd()',
                    'HTTP_PURGE_DATA': 'Y'})
    names = json.loads(result if isinstance(result, str) else result[0])
    assert set(names) <= {'appname', 'user_id', 'username'}
    assert 'filter_type' not in names and 'filter_value' not in names
    assert 'purge_data' not in names
