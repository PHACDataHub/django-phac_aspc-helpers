"""Related to Authentication"""
from django import template
from django.template import loader
from django.conf import settings

register = template.Library()


@register.simple_tag()
def phac_aspc_auth_signin_microsoft_button(query_params=""):
    """Returns a signin button using the microsoft design"""

    return (
        loader.get_template("phac_aspc/helpers/auth/buttons/microsoft.html").render({'query_params': query_params})
        if getattr(settings, "PHAC_ASPC_HELPER_OAUTH_PROVIDER", False)
        else ""
    )
