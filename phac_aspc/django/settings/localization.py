"""Recommended localization settings"""
from django.utils.translation import gettext_lazy as _

from .utils import global_from_env
from .localization_env import localization_env_config

LANGUAGES = (
    ("fr-ca", _("French")),
    ("en-ca", _("English")),
)

global_from_env(**localization_env_config)
