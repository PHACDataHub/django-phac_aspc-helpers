from phac_aspc.django.helpers.jinja_utils import include_from_dtl
from phac_aspc.jinja.registry import registry

registry.add_global("include_from_dtl", include_from_dtl)


def environment(**options):
    env = registry.get_environment(**options)
    return env
