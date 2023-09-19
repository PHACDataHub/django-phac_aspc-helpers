from django.template.loader import get_template
from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

register = template.Library()

is_django_templates_and_jinja_both_configured = map(
    lambda template_backend: next(
        filter(
            lambda tempalte_config: tempalte_config["BACKEND"].endswith(
                template_backend
            ),
            settings.TEMPLATES,
        ),
        False,
    ),
    ["DjangoTemplates", "Jinja2"],
)


@register.simple_tag(takes_context=True)
def phac_aspc_jinja_include(context, template_name):
    """Used to render a Jinja template inside a standard Django template.

    Requires your app to have both DjangoTemplates and Jinja2 template backends
    installed and configured for use.
    """

    if not is_django_templates_and_jinja_both_configured:
        raise ImproperlyConfigured(
            "settings.TEMPLATES must include both the DjangoTemplate and Jinja2 "
            + "backends for this tag to function!"
        )

    jinja_template = get_template(template_name)

    return jinja_template.render(context.flatten())
