"""This file contains utilities helpful for settings declarations"""
import inspect

import environ


def global_from_env(prefix="PHAC_ASPC_", **conf):
    """Create named global variables based on the provided environment variable
    scheme.  Variables defined in the scheme will be inserted into the calling
    module's globals and prefixed with `PHAC_ASPC_` when fetching the
    environment variable.

    prefix can be used to change the environment variable prefix that is added
    to the beginning on the variables defined in conf.  By default this value is
    `PHAC_ASPC_`.

    conf is a dictionary used to generate the scheme for django-environ.

    See https://django-environ.readthedocs.io/en/latest/api.html#environ.Env for
    additional information on the scheme.

    """

    mod = inspect.getmodule(inspect.stack()[1][0])

    scheme = {}
    for name, values in conf.items():
        scheme[f"{prefix}{name}"] = values

    env = environ.Env(**scheme)
    environ.Env.read_env()

    for name in conf:
        setattr(mod, name, env(f"{prefix}{name}"))
