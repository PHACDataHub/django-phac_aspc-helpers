"""Related to Authentication"""

from django import template
from django.template import loader

from phac_aspc.django.settings.security_env import get_oauth_env_value

register = template.Library()


@register.simple_tag()
def phac_aspc_auth_signin_microsoft_button(query_params=""):
    """Returns a signin button using the microsoft design"""

    return (
        loader.get_template("phac_aspc/helpers/auth/buttons/microsoft.html").render(
            {"query_params": query_params}
        )
        if "microsoft" in get_oauth_env_value("PROVIDERS")
        else ""
    )


@register.simple_tag()
def phac_aspc_auth_signin_secure_gateway_button(query_params=""):
    """Returns a signin button using the secure gateway design"""

    return (
        loader.get_template(
            "phac_aspc/helpers/auth/buttons/secure_gateway.html"
        ).render({"query_params": query_params})
        if "dev_secure_gateway" in get_oauth_env_value("PROVIDERS")
        else ""
    )
