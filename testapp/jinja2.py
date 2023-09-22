from jinja2 import Environment

from phac_aspc.django.helpers.jinja_utils import include_from_dtl


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            "include_from_dtl": include_from_dtl,
        }
    )
    return env
