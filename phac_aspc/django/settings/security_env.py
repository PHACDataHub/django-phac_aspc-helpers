"""Security and authentication configuration env var configs and getters"""
from phac_aspc.django.settings.utils.env_utils import get_env, get_env_value

oauth_env = get_env(
    OAUTH_PROVIDER=(str, ""),
    OAUTH_APP_CLIENT_ID=(str, ""),
    OAUTH_APP_CLIENT_SECRET=(str, ""),
    OAUTH_MICROSOFT_TENANT=(str, "common"),
    OAUTH_REDIRECT_ON_LOGIN=(str, ""),
    OAUTH_USE_BACKEND=(
        str,
        "phac_aspc.django.helpers.auth.backend.PhacAspcOAuthBackend",
    ),
)


def get_oauth_env_value(key):
    return get_env_value(oauth_env, f"OAUTH_{key}")


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
