"""Related to implementing WET"""
from django import template
from django.utils.translation import get_language

register = template.Library()


@register.simple_tag()
def phac_aspc_localization_lang():
    """Returns the current language code"""
    return get_language()


@register.simple_tag(takes_context=True)
def use_string(context, name, strings=None):
    """
    Loads the string from a template or via the variable dict `strings` if the
    `name` key is defined within.  This allows strings to be overridden in 2
    ways, either by user defined templates or via the render context.

    When `name` is not found in `strings`, the template name becomes:

    phac_aspc/helpers/strings/{name}.html

    """
    if strings and name in strings:
        return strings[name]

    return template.loader.get_template(
        f"phac_aspc/helpers/strings/{name}.html", using="django"
    ).render(context.flatten())
