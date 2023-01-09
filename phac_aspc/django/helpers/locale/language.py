"""Locale switching is global to the application, so we do it in a thread-safe
context so no other parts of the application are affected."""

import locale
import threading
from contextlib import contextmanager

from django.utils.translation import activate, get_language

from .code import get_language_code

LOCALE_LOCK = threading.Lock()


@contextmanager
def locale_lang(lang):
    """Isolate changing of a locale to the code block that requires it.

    Usage:

    with locale_lang('fr-ca'):
        <insert your code here>

    """
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        old_lang = get_language()
        try:
            code = get_language_code(lang)
            activate(lang)
            yield locale.setlocale(
                locale.LC_ALL, "fr_CA.UTF8" if code == "fr" else "en_CA.UTF8"
            )
        finally:
            locale.setlocale(locale.LC_ALL, saved)
            activate(old_lang)
