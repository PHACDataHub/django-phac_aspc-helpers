""" Make all templatetags available to things like Jinja"""
from .phac_aspc_localization import phac_aspc_localization_lang
from .phac_aspc_wet import (
    WET_CDN_ROOT,
    jsdelivr,
    phac_aspc_wet_css,
    phac_aspc_wet_scripts,
    phac_aspc_wet_session_timeout_dialog,
)

__all__ = [
    "phac_aspc_localization_lang",
    "WET_CDN_ROOT",
    "jsdelivr",
    "phac_aspc_wet_css",
    "phac_aspc_wet_scripts",
    "phac_aspc_wet_session_timeout_dialog",
]
