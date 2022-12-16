"""Related to implementing WET"""
from django import template
from django.utils.html import format_html, mark_safe
from django.templatetags.static import static
from django.conf import settings

import json

register = template.Library()

@register.simple_tag
def css(base_only=False):
    """Generate the CSS tags required for WET

    If base_only is True, only those classes required for library features
    will be included.  (For example displaying the session timeout dialog).

    This should be used in the HEAD section of your templates.
    """
    css_url = static('phac_aspc_helpers/base.css') if base_only \
        else static('phac_aspc_helpers/GCWeb/css/theme.css')
    no_script = static('phac_aspc_helpers/wet-boew/css/noscript.min.css')
    return format_html(
        (
            f"<link rel=\"stylesheet\" href=\"{css_url}\">"
            f"<noscript><link rel=\"stylesheet\" href=\"{no_script}\"></noscript>"
        )
    )

@register.simple_tag
def scripts(include_jquery=True):
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
    wet_js = static('phac_aspc_helpers/wet-boew/js/wet-boew.min.js')
    gcweb_js = static('phac_aspc_helpers/GCWeb/js/theme.min.js')
    return format_html(f"""
        {jquery}
        <script src="{ wet_js }"></script>
        <script src="{ gcweb_js }"></script>
    """)


@register.simple_tag(takes_context=True)
def session_timeout_dialog(context, logout_url, include_h1=False):
    """Displays a dialog to the user warning them their session is about
    to expire, with the option to continue or end their session

    WARNING: Wet expects your page to have at least 1 H1 element, if not
    this component will not behave properly.  For this reason the include_h1
    property can be set to True, which will include an empty one.
    """
    if not context['request'].user.is_authenticated:
        return ''

    session_alive = settings.SESSION_COOKIE_AGE * 1000
    time_before_expiry = session_alive - (3 * 60) if session_alive >= 300000 \
        else session_alive * 0.8
    conf = dict(
        inactivity=session_alive - time_before_expiry,
        reactionTime=time_before_expiry,
        sessionalive=session_alive,
        logouturl=logout_url
    )
    invisible_h1 = f"<h1 style=\"display: none\"> \
            Sessions timeout in {settings.SESSION_COOKIE_AGE / 60} minutes. \
        </h1>" if include_h1 else ''
    return format_html(
        "{}<span class=\"wb-sessto\" data-wb-sessto='{}'></span>",
        mark_safe(invisible_h1),
        mark_safe(json.dumps(conf))
    )
