"""
Bearer-token authentication against an external OAuth 2.0 provider.

A request carrying `Authorization: Bearer <token>` is authenticated by asking the provider whether the token
is active (RFC 7662 token introspection) and which user it belongs to; that user is then matched to a Hydra
user by username. Nothing here knows about any particular provider: HWI is the first, but any provider that
offers introspection and uses Hydra usernames will do.

Configuration (hydra_base config, section [oauth]):
    introspection_url   the provider's RFC 7662 endpoint. Bearer authentication is off while this is unset.
    client_id           credentials hydra-server presents to the introspection endpoint (HTTP Basic)
    client_secret
    username_field      member of the introspection response holding the Hydra username (default: username)
    required_scope      optional scope the token must carry
    cache_seconds       how long an 'active' answer is trusted (default 30; the token's own expiry caps it)
    timeout             seconds to wait for the provider (default 5)

Any failure (provider unreachable, inactive token, unknown user) means the request is not authenticated.
"""
import hashlib
import logging
import threading
import time

import requests

from hydra_base import config
from hydra_base import db
from hydra_base.db.model import User

log = logging.getLogger(__name__)

_cache = {}
_cache_lock = threading.Lock()
_CACHE_MAX = 2048


def enabled():
    return bool(config.get('oauth', 'introspection_url', None))


def token_from_header(value):
    """ The token in an `Authorization: Bearer <token>` header value, or None. """
    if not value:
        return None
    scheme, _, token = value.strip().partition(' ')
    if scheme.lower() != 'bearer' or not token.strip():
        return None
    return token.strip()


def _cache_key(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def _introspect(token):
    """ Ask the provider about the token. Returns the response dict, or None if it could not be asked. """
    url = config.get('oauth', 'introspection_url')
    client_id = config.get('oauth', 'client_id', None)
    auth = (client_id, config.get('oauth', 'client_secret', '')) if client_id else None
    try:
        resp = requests.post(url, data={'token': token, 'token_type_hint': 'access_token'}, auth=auth,
                             timeout=float(config.get('oauth', 'timeout', 5)))
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.error("Token introspection at %s failed: %s", url, e)
        return None


def username_for_token(token):
    """ The Hydra username a bearer token belongs to, or None if it is not valid. """
    key = _cache_key(token)
    now = time.time()
    with _cache_lock:
        hit = _cache.get(key)
        if hit and hit[1] > now:
            return hit[0]

    data = _introspect(token)
    if not data or not data.get('active'):
        return None

    required = config.get('oauth', 'required_scope', None)
    if required and required not in str(data.get('scope', '')).split():
        log.info("Token lacks required scope %r", required)
        return None

    username = data.get(config.get('oauth', 'username_field', 'username'))
    if not username:
        return None

    ttl = float(config.get('oauth', 'cache_seconds', 30))
    if data.get('exp'):
        ttl = min(ttl, float(data['exp']) - now)
    if ttl > 0:
        with _cache_lock:
            if len(_cache) >= _CACHE_MAX:
                _cache.clear()
            _cache[key] = (username, now + ttl)
    return username


def authenticate(header_value):
    """
        Authenticate an Authorization header value. Returns (user_id, username) for a valid bearer
        token belonging to a known Hydra user, otherwise None.
    """
    token = token_from_header(header_value)
    if token is None or not enabled():
        return None
    username = username_for_token(token)
    if username is None:
        return None
    user = db.DBSession.query(User).filter(User.username == username).first()
    if user is None:
        log.info("Token is for %r, who is not a Hydra user", username)
        return None
    return user.id, user.username
