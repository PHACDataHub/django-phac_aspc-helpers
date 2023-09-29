from xml.etree import ElementTree

from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def phac_aspc_inline_svg(static_file_path=None, **kwargs):
    """Inlines a SVG icon from linkcube/src/core/assets/templates/core.assets/icon

    Based on https://stackoverflow.com/a/68802035

    Example usage:
        {% phac_aspc_inline_svg "phac_aspc_helpers/phac_logos/en.svg" height="2rem" %}
    Parameter: static_file_path
        Path of the svg to be inlined; resolved relative to the static root(s) of installed apps.
    Parameter: kwargs
        Additional kwargs are treated as attribute:value pairs and set on the svg's root node.
    Returns:
        stringified XML to be inlined, i.e.:
        '<svg class="..." height="...">...</svg>'
    """
    ElementTree.register_namespace("", "http://www.w3.org/2000/svg")

    svg_root = ElementTree.parse(finders.find(static_file_path)).getroot()

    for attribute, value in kwargs.items():
        svg_root.set(attribute, value)

    svg_string = ElementTree.tostring(svg_root, encoding="unicode", method="html")

    return mark_safe(svg_string)
