"""Recommended values related to security controls"""
from .utils import global_from_env, configure_authentication_backends

#  AC-7 Automatic lockout of users after invalid login attempts
AUTHENTICATION_BACKENDS = configure_authentication_backends([
    'django.contrib.auth.backends.ModelBackend',
])

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
    'HTTP_X_FORWARDED_FOR',
    'REMOTE_ADDR',
]

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
