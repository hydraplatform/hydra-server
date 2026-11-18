"""
    The login RPC must not log credentials and must not reveal why a login failed.
"""
import logging

import pytest

pytest.importorskip("spyne")
pytest.importorskip("hydra_base")

import hydra_base as hb
from hydra_base.exceptions import (HydraLoginUserNotFound, HydraLoginUserPasswordWrong,
                                   HydraLoginUserMaxAttemptsExceeded)
from hydra_server.server import service
from hydra_server.server.service import AuthenticationService, AuthenticationError

PASSWORD = "S3cret-p@ssw0rd-do-not-log"


class FakeTransport:
    pass


class FakeCtx:
    transport = FakeTransport()


def _login(monkeypatch, result):
    def fake_login_user(username, password):
        if isinstance(result, Exception):
            raise result
        return result
    monkeypatch.setattr(hb.hdb, "login_user", fake_login_user)
    return AuthenticationService.login(FakeCtx(), "someone", PASSWORD)


def test_password_is_never_logged(monkeypatch, caplog):
    with caplog.at_level(logging.DEBUG):
        for outcome in (7, HydraLoginUserPasswordWrong("someone"), HydraLoginUserNotFound("someone")):
            try:
                _login(monkeypatch, outcome)
            except AuthenticationError:
                pass
    assert PASSWORD not in caplog.text


@pytest.mark.parametrize("cause", [
    HydraLoginUserNotFound("someone"),
    HydraLoginUserPasswordWrong("someone"),
    HydraLoginUserMaxAttemptsExceeded("Max login attempts exceeded for user someone"),
])
def test_every_failure_gives_the_same_message(monkeypatch, cause):
    with pytest.raises(AuthenticationError) as exc:
        _login(monkeypatch, cause)
    assert exc.value.faultstring == service.GENERIC_LOGIN_FAILURE
    assert exc.value.message == service.GENERIC_LOGIN_FAILURE
    assert "someone" not in exc.value.faultstring


def test_successful_login_still_returns_the_user(monkeypatch):
    response = _login(monkeypatch, 7)
    assert response.user_id == 7
    assert response.username == "someone"


def test_bytes_credentials_are_decoded(monkeypatch):
    seen = {}
    monkeypatch.setattr(hb.hdb, "login_user", lambda u, p: seen.update(u=u, p=p) or 1)
    AuthenticationService.login(FakeCtx(), b"someone", b"pw")
    assert seen == {"u": "someone", "p": "pw"}
