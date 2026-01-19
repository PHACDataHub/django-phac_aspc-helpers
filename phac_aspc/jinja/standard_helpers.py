from urllib.parse import quote, urlencode, urlparse, urlunparse

from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import activate, get_language, override

from jinja2 import pass_context
from jinja2.ext import Extension, nodes

import phac_aspc.django.helpers.templatetags as phac_aspc
from phac_aspc.jinja.registry import registry as r

# basic python builtins
r.add_global("getattr", getattr)
r.add_global("hasattr", hasattr)
r.add_global("len", len)
r.add_global("list", list)
r.add_global("print", print)
r.add_global("True", True)
r.add_global("False", False)


# django helpers
r.add_global("static", static)
r.add_global("phac_aspc", phac_aspc)
r.add_global("urlencode", urlencode)
r.add_global("url", reverse)


@r.add_extension
class LanguageExtension(Extension):
    """
    manually override language for a block, e.g. :
        {% language 'fr-ca' %}
        <p>{{ _("Hello") }}</p>
        {% endlanguage %}
    """

    tags = {"language"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        # Parse the language code argument
        args = [parser.parse_expression()]
        # Parse everything between the start and end tag:
        body = parser.parse_statements(["name:endlanguage"], drop_needle=True)
        # Call the _switch_language method with the given language code and body
        return nodes.CallBlock(
            self.call_method("_switch_language", args), [], [], body
        ).set_lineno(lineno)

    def _switch_language(self, language_code, caller):
        with override(language_code):
            # Temporarily override the active language and render the body
            output = caller()
        return output


@r.add_global
def convert_url_other_lang(url_str):
    parsed_url = urlparse(url_str)
    path = parsed_url.path
    query = parsed_url.query

    if "fr-ca" in path:
        new_path = path.replace("/fr-ca", "")
    else:
        new_path = "/fr-ca" + path

    new_url = parsed_url._replace(path=new_path)

    if "login" in path and "next" in query:
        if "fr-ca" in path:
            new_query = query.replace("next=/fr-ca", "next=")
        else:
            new_query = query.replace("next=", "next=/fr-ca")
    else:
        new_query = query

    new_url = new_url._replace(query=new_query)

    return urlunparse(new_url)


@r.add_global
@pass_context
def url_to_other_lang(context):
    """
    Provides the URL to the other language:
    For example, if current language is English then it will provide
    the url to the French language.
    """
    request = context["request"]
    full_uri = request.get_full_path()
    return convert_url_other_lang(full_uri)


@r.add_global
def get_lang_code():
    """
    Provides the language code (en-ca or fr-ca) for the current language
    """
    current_lang = get_language()
    return current_lang.lower()


@r.add_global
def get_other_lang_code():
    """
    Provides the language code (en-ca or fr-ca) for the other language (Ex. if current lang
    is en-ca, then the other lang is fr-ca), this is currently used for
    setting the lang tag in the button switch UI
    """
    current_lang = get_language()
    if "en" in current_lang.lower():
        return "fr-ca"
    return "en-ca"


@r.add_global
def get_other_lang():
    """
    Returns the language label ("Français" or "English") for the other language not currently being used.
    """
    current_lang = get_language()
    if "en" in current_lang.lower():
        return "Français"
    return "English"


@r.add_global
@pass_context
def ipython(context):
    import IPython

    IPython.embed()
    return ""


@r.add_global
def cls_str(*args, **kwargs):
    """
    Utility for manipulating many class names
    padds a space to the beginning and end of the string
    """

    args_str = " ".join(str(arg) for arg in args if arg)
    kwargs_str = " ".join(k for k, v in kwargs.items() if v and k)

    s = ""

    if args_str:
        s += " " + args_str

    if kwargs_str:
        s += " " + kwargs_str

    if not s:
        return ""

    return s + " "


@r.add_global
@pass_context
def respects_rule(context, rule, obj=None):
    from phac_aspc.rules import test_rule

    user = context["request"].user
    if not user.is_authenticated:
        return False
    return test_rule(rule, user, obj)
