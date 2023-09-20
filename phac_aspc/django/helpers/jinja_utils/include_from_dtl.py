from django.template.loader import get_template

from jinja2 import pass_context

from phac_aspc.django.helpers.jinja_dtl_interop_utils import (
    assert_both_dtl_and_jinja_configured,
)


@pass_context
def include_from_dtl(context, template_name):
    """
    Renders a DTL template inside a Jinja2 template, using the Jinja2 template's context.
    """
    assert_both_dtl_and_jinja_configured()

    dtl_template = get_template(template_name)

    return dtl_template.render(context.get_all())
