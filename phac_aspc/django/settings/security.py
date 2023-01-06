"""Recommended values related to security controls"""
from .utils import global_from_env

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
