"""
Localization templatetags unit tests
"""
from phac_aspc.django.helpers.templatetags.phac_aspc_localization import get_language
from phac_aspc.django.helpers.locale.language import locale_lang


def test_get_language():
    """
    Test the get_language template tag returns the correct information
    """
    with locale_lang("fr-ca"):
        assert get_language() == "fr-ca"

    with locale_lang("en-ca"):
        assert get_language() == "en-ca"
