# flake8: noqa
"""
Localization templatetags unit tests
"""
import pytest

from django.test import override_settings
from django.core.exceptions import ImproperlyConfigured

from phac_aspc.django.helpers.templatetags.phac_aspc_wet import (
    jsdelivr,
    phac_aspc_wet_css,
    phac_aspc_wet_scripts,
    phac_aspc_wet_session_timeout_dialog,
)

urlpatterns = []


class Request:  # pylint: disable=too-few-public-methods
    """Mock request object"""

    user = None

    def __init__(self, user):
        self.user = user


class User:  # pylint: disable=too-few-public-methods
    """Mock user object"""

    is_authenticated = False

    def __init__(self, auth=False):
        self.is_authenticated = auth


@override_settings(WET_VERSION="test.testing", THEME_VERSION="theme.version")
def test_jsdelivr():
    """
    Test the get_language template tag returns the correct information
    """

    assert (
        jsdelivr("wet-boew", "test.js")
        == "https://cdn.jsdelivr.net/gh/wet-boew/wet-boew-dist@test.testing/test.js"
    )

    assert (
        jsdelivr("some-other", "test.js")
        == "https://cdn.jsdelivr.net/gh/wet-boew/some-other-dist@theme.version/test.js"
    )


@override_settings(WET_VERSION="a", THEME_VERSION="b")
def test_phac_aspc_wet_css():
    """Test CSS tag generator"""
    html = phac_aspc_wet_css()
    assert html == (
        '<link rel="stylesheet" '
        'href="https://cdn.jsdelivr.net/gh/wet-boew/themes-dist@b/'
        'GCWeb/css/theme.min.css">'
        "<noscript>"
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/wet-boew/'
        'wet-boew-dist@a/wet-boew/css/noscript.min.css">'
        "</noscript>"
    )

    html_only_base = phac_aspc_wet_css(base_only=True)
    assert html_only_base == (
        '<link rel="stylesheet" '
        'href="phac_aspc_helpers/base.css">'
        "<noscript>"
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/wet-boew/'
        'wet-boew-dist@a/wet-boew/css/noscript.min.css">'
        "</noscript>"
    )


@override_settings(WET_VERSION="a", THEME_VERSION="b")
def test_phac_aspc_wet_scripts():
    """Test script tag generator"""
    assert (
        phac_aspc_wet_scripts()
        == """
        
      <script
        src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js"
        integrity="sha384-rY/jv8mMhqDabXSo+UCggqKtdmBfd3qC2/KvyTDNQ6PcUJXaxK1tMepoQda4g5vB"
        crossorigin="anonymous"
      ></script>
        <script src="https://cdn.jsdelivr.net/gh/wet-boew/wet-boew-dist@a/wet-boew/js/wet-boew.min.js"></script>
        <script src="https://cdn.jsdelivr.net/gh/wet-boew/themes-dist@b/GCWeb/js/theme.min.js"></script>
    """
    )

    assert (
        phac_aspc_wet_scripts(include_jquery=False)
        == """
        
        <script src="https://cdn.jsdelivr.net/gh/wet-boew/wet-boew-dist@a/wet-boew/js/wet-boew.min.js"></script>
        <script src="https://cdn.jsdelivr.net/gh/wet-boew/themes-dist@b/GCWeb/js/theme.min.js"></script>
    """
    )


@override_settings(
    SESSION_COOKIE_AGE=60,
    ROOT_URLCONF="phac_aspc.django.helpers.urls",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,
        },
    ],
)
def test_phac_aspc_wet_session_timeout_dialog():
    """Test session timeout dialog template tag"""
    context_logged_in = {"request": Request(User(True))}
    context_logged_out = {"request": Request(User())}
    assert phac_aspc_wet_session_timeout_dialog(context_logged_out, "test_logout") == ""
    html = phac_aspc_wet_session_timeout_dialog(context_logged_in, "test_logout")
    assert "&quot;logouturl&quot;: &quot;test_logout&quot;" in html
    assert "&quot;inactivity&quot;: 48000.0" in html
    assert "&quot;reactionTime&quot;: 12000.0" in html
    assert "&quot;sessionalive&quot;: 60000" in html


@override_settings(
    SESSION_COOKIE_AGE=60,
    ROOT_URLCONF=__name__,
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,
        },
    ],
)
def test_phac_aspc_wet_session_timeout_dialog_errors():
    """Test session timeout dialog template tag"""
    with pytest.raises(ImproperlyConfigured):
        phac_aspc_wet_session_timeout_dialog(
            {"request": Request(User(True))}, "test_logout"
        )
