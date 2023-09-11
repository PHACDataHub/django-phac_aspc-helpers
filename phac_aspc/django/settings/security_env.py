"""Security and authentication configuration env var configs and getters"""
from phac_aspc.django.settings.utils.env_utils import (
    PHAC_ENV_PREFIX,
    get_env,
    get_env_value,
)

OAUTH_ENV_PREFIX = f"{PHAC_ENV_PREFIX}OAUTH_"

oauth_env = get_env(
    prefix=OAUTH_ENV_PREFIX,
    PROVIDER=(str, ""),
    APP_CLIENT_ID=(str, ""),
    APP_CLIENT_SECRET=(str, ""),
    MICROSOFT_TENANT=(str, "common"),
    REDIRECT_ON_LOGIN=(str, ""),
    USE_BACKEND=(
        str,
        "phac_aspc.django.helpers.auth.backend.PhacAspcOAuthBackend",
    ),
)


def get_oauth_env_value(key):
    return get_env_value(oauth_env, key, prefix=OAUTH_ENV_PREFIX)


security_env_config = {
    # ----- AC-11 - Session controls
    # Sessions expire in 20 minutes
    "SESSION_COOKIE_AGE": (int, 1200),
    # Use HTTPS for session cookie
    "SESSION_COOKIE_SECURE": (bool, True),
    # Sessions close when browser is closed
    "SESSION_EXPIRE_AT_BROWSER_CLOSE": (bool, True),
    # Every requests extends the session (This is required for the WET session
    # plugin to function properly.)
    "SESSION_SAVE_EVERY_REQUEST": (bool, True),
}
