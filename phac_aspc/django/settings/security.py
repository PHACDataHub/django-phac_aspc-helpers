"""Recommended values related to security controls"""
from django.core.exceptions import ImproperlyConfigured

from .utils import (
    global_from_env,
    configure_authentication_backends,
)

from .security_env import get_oauth_env_value, security_env_config

# Lockout users based on their (username, IP address) combinations
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]

# Log unsuccessful logins
AXES_ENABLE_ACCESS_FAILURE_LOG = True

# After 3 failed login attempts, lock out the combination (IP + user).
AXES_FAILURE_LIMIT = 3

# After 30 minutes, locked out accounts are automatically unlocked.
AXES_COOLOFF_TIME = 0.5

# Reverse proxy configuration
AXES_IPWARE_PROXY_COUNT = 1  # (Behind 1 proxy)
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    "HTTP_X_FORWARDED_FOR",
    "REMOTE_ADDR",
]

# Configure the identity provider if the `{PREFIX}OAUTH_PROVIDER`
# `environment variable is set.

if get_oauth_env_value("PROVIDER") == "microsoft":
    provider = get_oauth_env_value("PROVIDER")
    client_id = get_oauth_env_value("APP_CLIENT_ID")
    client_secret = get_oauth_env_value("APP_CLIENT_SECRET")
    tenant = get_oauth_env_value("MICROSOFT_TENANT")

    if client_id == "":
        raise ImproperlyConfigured("settings.OAUTH_APP_CLIENT_ID is required.")

    if client_secret == "":
        raise ImproperlyConfigured("settings.OAUTH_APP_CLIENT_SECRET is required.")

    AUTHLIB_OAUTH_CLIENTS = {
        f"{provider}": {
            "client_id": client_id,
            "client_secret": client_secret,
            "server_metadata_url": f"https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration",  # pylint: disable=line-too-long  # noqa: E501
            "client_kwargs": {
                "scope": "openid email profile",
            },
        }
    }

#  AC-7 Automatic lockout of users after invalid login attempts
AUTHENTICATION_BACKENDS = configure_authentication_backends(
    [
        "django.contrib.auth.backends.ModelBackend",
    ]
)

#  AC-11 - Session controls set via security_env_config
global_from_env(**security_env_config)
