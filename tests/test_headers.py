"""
    Request headers are only accepted for declared fields.

    headers.py is loaded by path so that these tests do not need spyne.
"""
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parents[1] / "hydra_server" / "server" / "headers.py"
_spec = importlib.util.spec_from_file_location("hydra_server_headers", _path)
headers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(headers)


def _doc(**fields):
    """ ctx.in_header_doc has the form {name: [value]} """
    return {k: [v] for k, v in fields.items()}


def test_declared_fields_are_kept():
    doc = _doc(username="alice", user_id="3", appname="Test App", app_name="Test App")
    assert headers.filter_header_fields(doc) == {
        "username": "alice", "user_id": "3", "appname": "Test App", "app_name": "Test App"}


def test_other_headers_are_dropped():
    doc = _doc(appname="x", filter_type="id", filter_value="1", host="example.org",
               cookie="a=b", include_data="n", purge_data="Y")
    assert headers.filter_header_fields(doc) == {"appname": "x"}


def test_empty_header_doc():
    assert headers.filter_header_fields({}) == {}


def test_names_are_matched_exactly():
    doc = _doc(Username="a", USER_ID="1", user_id_="2", _appname="3")
    assert headers.filter_header_fields(doc) == {}
