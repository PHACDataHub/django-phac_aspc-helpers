from django import template
from django.template.loader import get_template

from phac_aspc.django.helpers.jinja_dtl_interop_utils import (
    assert_both_dtl_and_jinja_configured,
)

register = template.Library()


@register.simple_tag(takes_context=True)
def phac_aspc_include_from_jinja(context, template_name):
    """
    Renders a Jinja2 template inside a DTL template, using the DTL template's context.
    """
    assert_both_dtl_and_jinja_configured()

    jinja_template = get_template(template_name)

    return jinja_template.render(context.flatten())
