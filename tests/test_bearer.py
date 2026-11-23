"""
Unit tests for bearer-token authentication (hydra_server.server.bearer). The OAuth provider and the user
table are replaced, so these need neither a database nor a running provider.
"""
import time

import pytest

from hydra_server.server import bearer


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    bearer._cache.clear()
    settings = {'introspection_url': 'http://provider.test/introspect'}
    from hydra_base import config
    monkeypatch.setattr(config, 'get', lambda section, option, default=None: settings.get(option, default) if section == 'oauth' else default)
    return settings


def _provider(monkeypatch, response):
    calls = []
    def fake(token):
        calls.append(token)
        return response
    monkeypatch.setattr(bearer, '_introspect', fake)
    return calls


@pytest.mark.parametrize('value,expected', [
    ('Bearer abc', 'abc'), ('bearer abc', 'abc'), ('BEARER  abc ', 'abc'),
    ('Basic abc', None), ('Bearer', None), ('Bearer ', None), ('', None), (None, None),
])
def test_token_from_header(value, expected):
    assert bearer.token_from_header(value) == expected


def test_disabled_without_introspection_url(_clean, monkeypatch):
    _clean.clear()
    calls = _provider(monkeypatch, {'active': True, 'username': 'a@b'})
    assert bearer.authenticate('Bearer abc') is None
    assert calls == []


def test_active_token_gives_username(monkeypatch):
    _provider(monkeypatch, {'active': True, 'username': 'a@b'})
    assert bearer.username_for_token('t') == 'a@b'


def test_inactive_token_is_refused(monkeypatch):
    _provider(monkeypatch, {'active': False})
    assert bearer.username_for_token('t') is None


def test_provider_unreachable_fails_closed(monkeypatch):
    _provider(monkeypatch, None)
    assert bearer.username_for_token('t') is None


def test_active_answer_is_cached(monkeypatch):
    calls = _provider(monkeypatch, {'active': True, 'username': 'a@b'})
    bearer.username_for_token('t')
    bearer.username_for_token('t')
    assert calls == ['t']


def test_inactive_answer_is_not_cached(monkeypatch):
    calls = _provider(monkeypatch, {'active': False})
    bearer.username_for_token('t')
    bearer.username_for_token('t')
    assert calls == ['t', 't']


def test_expiry_caps_the_cache(monkeypatch):
    calls = _provider(monkeypatch, {'active': True, 'username': 'a@b', 'exp': time.time() - 5})
    assert bearer.username_for_token('t') == 'a@b'   # answered, but already expired: not cached
    bearer.username_for_token('t')
    assert len(calls) == 2


def test_required_scope(_clean, monkeypatch):
    _clean['required_scope'] = 'hydra'
    _provider(monkeypatch, {'active': True, 'username': 'a@b', 'scope': 'profile'})
    assert bearer.username_for_token('t') is None
    bearer._cache.clear()
    _provider(monkeypatch, {'active': True, 'username': 'a@b', 'scope': 'profile hydra'})
    assert bearer.username_for_token('t') == 'a@b'


def test_username_field(_clean, monkeypatch):
    _clean['username_field'] = 'email'
    _provider(monkeypatch, {'active': True, 'email': 'e@x'})
    assert bearer.username_for_token('t') == 'e@x'


def test_authenticate_maps_to_hydra_user(monkeypatch):
    _provider(monkeypatch, {'active': True, 'username': 'a@b'})

    class _User:
        id, username = 7, 'a@b'

    class _Q:
        def __init__(self, user): self.user = user
        def filter(self, *a): return self
        def first(self): return self.user

    class _Session:
        user = _User()
        def query(self, model): return _Q(self.user)

    # DBSession only exists once hydra-base has connected, so it must be looked up at call time
    monkeypatch.setattr(bearer.db, 'DBSession', _Session())
    assert bearer.authenticate('Bearer t') == (7, 'a@b')
    _Session.user = None
    assert bearer.authenticate('Bearer t') is None   # a valid token for someone who is not a Hydra user
