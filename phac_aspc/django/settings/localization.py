"""Recommended localization settings"""
from django.utils.translation import gettext_lazy as _

from .utils import global_from_env

LANGUAGES = (
    ("fr-ca", _("French")),
    ("en-ca", _("English")),
)

global_from_env(
    LANGUAGE_CODE=(str, "en-ca"),
)
