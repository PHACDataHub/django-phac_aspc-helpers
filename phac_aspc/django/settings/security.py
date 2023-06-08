"""Recommended values related to security controls"""
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from .utils import (
    global_from_env,
    get_env,
    get_env_value,
    configure_authentication_backends,
)

# Lockout users based on their username and IP address
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True

# Log unsuccessful logins
AXES_ENABLE_ACCESS_FAILURE_LOG = True

# After 3 failed login attempts, lock out the combination (IP + user).
AXES_FAILURE_LIMIT = 3

# After 30 minutes, locked out accounts are automatically unlocked.
AXES_COOLOFF_TIME = 0.5

# Reverse proxy configuration
AXES_PROXY_COUNT = 1  # (Behind 1 proxy)
AXES_META_PRECEDENCE_ORDER = [
    "HTTP_X_FORWARDED_FOR",
    "REMOTE_ADDR",
]

# Configure the identity provider if the `{PREFIX}OAUTH_PROVIDER`
# `environment variable is set.
auth_config = get_env(
    OAUTH_PROVIDER=(str, ""),
    OAUTH_APP_CLIENT_ID=(str, ""),
    OAUTH_APP_CLIENT_SECRET=(str, ""),
    OAUTH_MICROSOFT_TENANT=(str, "common"),
)

if get_env_value(auth_config, "OAUTH_PROVIDER") == "microsoft":
    provider = get_env_value(auth_config, "OAUTH_PROVIDER")
    client_id = get_env_value(auth_config, "OAUTH_APP_CLIENT_ID")
    client_secret = get_env_value(auth_config, "OAUTH_APP_CLIENT_SECRET")
    tenant = get_env_value(auth_config, "OAUTH_MICROSOFT_TENANT")

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

    PHAC_ASPC_OAUTH_USE_BACKEND = getattr(
        settings,
        "PHAC_ASPC_OAUTH_USE_BACKEND",
        "phac_aspc.django.helpers.auth.backend.PhacAspcOAuthBackend",
    )
    settings.PHAC_ASPC_OAUTH_USE_BACKEND = PHAC_ASPC_OAUTH_USE_BACKEND
    PHAC_ASPC_HELPER_OAUTH_PROVIDER = provider

#  AC-7 Automatic lockout of users after invalid login attempts
AUTHENTICATION_BACKENDS = configure_authentication_backends(
    [
        "django.contrib.auth.backends.ModelBackend",
    ]
)

#  AC-11 - Session controls
global_from_env(
    # Sessions expire in 20 minutes
    SESSION_COOKIE_AGE=(int, 1200),
    # Use HTTPS for session cookie
    SESSION_COOKIE_SECURE=(bool, True),
    # Sessions close when browser is closed
    SESSION_EXPIRE_AT_BROWSER_CLOSE=(bool, True),
    # Every requests extends the session (This is required for the WET session
    # plugin to function properly.)
    SESSION_SAVE_EVERY_REQUEST=(bool, True),
)
