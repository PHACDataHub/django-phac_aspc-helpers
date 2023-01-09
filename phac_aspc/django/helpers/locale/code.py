"""Utility to get language code from lang strings with locales"""
from django.utils.translation import get_language, get_language_info


def get_language_code(lang=None):
    """Translate strings like fr-ca, en-ca to fr and en respectively
    If lang is not specified the current active language will be used.
    """
    if not lang:
        lang = get_language()
    try:
        return get_language_info(lang)["code"]
    except TypeError:
        return "en"
