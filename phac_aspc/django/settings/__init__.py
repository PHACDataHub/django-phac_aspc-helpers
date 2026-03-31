# flake8: noqa
"""Settings module"""

import secrets

from .localization import *
from .logging import *
from .security import *
from .wet import *

STATIC_BUST_TOKEN = secrets.token_hex(
    # used to bust cache, change on each  deploy/app restart
    # e.g. static(site.js)?v={settings.STATIC_BUST_TOKEN}
    4
)
