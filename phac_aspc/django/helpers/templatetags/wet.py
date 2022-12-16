"""Related to implementing WET"""
from django import template
from django.utils.html import format_html, mark_safe
from django.templatetags.static import static

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
    gcweb_js = static('phac_aspc_helpers/GCWeb/js/1theme.min.js')
    return format_html(f"""
        {jquery}
        <script src="{ wet_js }"></script>
        <script src="{ gcweb_js }"></script>
    """)


@register.simple_tag
def session_timeout_dialog():
    conf = dict(
        inactivity=5000,
        logouturl="/"
    )
    return format_html(
        "<span class=\"wb-sessto\" data-wb-sessto='{}'></span>",
        mark_safe(json.dumps(conf))
    )
