""" Make all templatetags available to things like Jinja"""
from .phac_aspc_localization import phac_aspc_localization_lang
from .phac_aspc_wet import (
    WET_CDN_ROOT,
    jsdelivr,
    phac_aspc_wet_css,
    phac_aspc_wet_scripts,
    phac_aspc_wet_session_timeout_dialog,
)
from .phac_aspc_auth import phac_aspc_auth_signin_microsoft_button
from .phac_aspc_include_from_jinja import phac_aspc_include_from_jinja
from .phac_aspc_inline_svg import phac_aspc_inline_svg

__all__ = [
    "phac_aspc_localization_lang",
    "WET_CDN_ROOT",
    "jsdelivr",
    "phac_aspc_wet_css",
    "phac_aspc_wet_scripts",
    "phac_aspc_wet_session_timeout_dialog",
    "phac_aspc_auth_signin_microsoft_button",
    "phac_aspc_include_from_jinja",
    "phac_aspc_inline_svg",
]
