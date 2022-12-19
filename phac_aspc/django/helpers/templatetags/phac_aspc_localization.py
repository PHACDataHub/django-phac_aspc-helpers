"""Related to implementing WET"""
from django import template
from django.utils.translation import to_locale, get_language
    

register = template.Library()

@register.simple_tag()
def phac_aspc_localization_lang():
    """Returns the current language code"""
    return get_language()
    