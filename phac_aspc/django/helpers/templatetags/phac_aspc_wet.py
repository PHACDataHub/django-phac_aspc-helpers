"""Related to implementing WET"""
import json

from django import template
from django import urls
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import loader
from django.templatetags.static import static
from django.urls.exceptions import NoReverseMatch
from django.utils.html import format_html

register = template.Library()

WET_CDN_ROOT = 'https://cdn.jsdelivr.net/gh/wet-boew'


def jsdelivr(pkg, asset):
    """Construct a jsdelivr CDN URL for the provided WET package and asset."""
    ver = settings.WET_VERSION if pkg == 'wet-boew' else settings.THEME_VERSION
    return f"{WET_CDN_ROOT}/{pkg}-dist@{ver}/{asset}"


@register.simple_tag
def phac_aspc_wet_css(base_only=False):
    """Generate the CSS tags required for WET

    If base_only is True, only those classes required for library features
    will be included.  (For example displaying the session timeout dialog).

    This should be used in the HEAD section of your templates.
    """
    css_url = static('phac_aspc_helpers/base.css') if base_only \
        else jsdelivr('themes', 'GCWeb/css/theme.min.css')
    no_script = jsdelivr('wet-boew', 'wet-boew/css/noscript.min.css')
    return format_html(
        (
            f"<link rel=\"stylesheet\" href=\"{css_url}\">"
            f"<noscript><link rel=\"stylesheet\" href=\"{no_script}\"></noscript>"
        )
    )

@register.simple_tag
def phac_aspc_wet_scripts(include_jquery=True):
    """Generate the script tags required for WET

    If include_jquery is False, jquery will not be included

    This should be used directly before the closing </body> tag in your
    templates.
    """
    jquery = """
      <script
        src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js"
        integrity="sha384-rY/jv8mMhqDabXSo+UCggqKtdmBfd3qC2/KvyTDNQ6PcUJXaxK1tMepoQda4g5vB"
        crossorigin="anonymous"
      ></script>""" if include_jquery else ''
    wet_js = jsdelivr('wet-boew', 'wet-boew/js/wet-boew.min.js')
    gcweb_js = jsdelivr('themes', 'GCWeb/js/theme.min.js')
    return format_html(f"""
        {jquery}
        <script src="{ wet_js }"></script>
        <script src="{ gcweb_js }"></script>
    """)


@register.simple_tag(takes_context=True)
def phac_aspc_wet_session_timeout_dialog(context, logout_url):
    """Displays a dialog to the user warning them their session is about
    to expire, with the option to continue or end their session

    WARNING: Wet expects your page to have at least 1 H1 element, if not
    this component will not behave properly.  For this reason if no h1 is
    present one is automatically appended to the document with its display set
    to none.
    """
    if not context['request'].user.is_authenticated:
        return ''

    session_alive = settings.SESSION_COOKIE_AGE * 1000
    reaction_time = 180000 if session_alive >= 300000 else session_alive * 0.2

    logouturl = logout_url
    try:
        logouturl = urls.reverse(logout_url)
    except NoReverseMatch:
        pass


    try:
        return loader.get_template(
            "phac_aspc/helpers/wet/session_timeout.html"
        ).render(
            dict(
                config=json.dumps(dict(
                    inactivity=session_alive - reaction_time,
                    reactionTime=reaction_time,
                    refreshCallbackUrl=urls.reverse('phac_aspc_helpers_session'),
                    method='PUT',
                    sessionalive=session_alive,
                    logouturl=logouturl
                ))
            ),
            request=context['request']
        )
    except NoReverseMatch as exc:
        raise ImproperlyConfigured("The WET urls are not loaded.  See README") from exc
