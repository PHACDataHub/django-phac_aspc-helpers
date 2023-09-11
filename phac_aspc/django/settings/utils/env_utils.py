"""This file contains utilities for accessing env values used by consuming libraries 
to configure PHAC helpers' behaviour
"""
import os
import inspect

import environ

from django.conf import settings


def get_env_value(env, key, prefix="PHAC_ASPC_"):
    """Returns the value for the prefixed key from the provided env, unless that
    key exists in the Django settings in which case the settings value is used
    """

    prefixed_key = f"{prefix}{key}"

    return getattr(
        settings,
        prefixed_key,
        env(prefixed_key),
    )


def get_env(prefix="PHAC_ASPC_", **conf):
    """Return django-environ configured with the provided values and
    using the prefix.

    prefix can be used to change the environment variable prefix that is added
    to the beginning on the variables defined in conf.  By default this value is
    `PHAC_ASPC_`.

    conf is a dictionary used to generate the scheme for django-environ.

    See https://django-environ.readthedocs.io/en/latest/api.html#environ.Env for
    additional information on the scheme.
    """

    def _find_env_file(path):
        # look for .env file in provided path
        filename = os.path.join(path, ".env")
        if os.path.isfile(filename):
            return filename

        # search the parent
        parent = os.path.dirname(path)
        if parent and os.path.normcase(parent) != os.path.normcase(
            os.path.abspath(os.sep)
        ):
            return _find_env_file(parent)

        # Not found
        return ""

    scheme = {}
    for name, values in conf.items():
        scheme[f"{prefix}{name}"] = values

    env = environ.Env(**scheme)
    environ.Env.read_env(_find_env_file(os.path.abspath(os.path.dirname(__name__))))
    return env


def global_from_env(prefix="PHAC_ASPC_", **conf):
    """Create named global variables based on the provided environment variable
    scheme.  Variables defined in the scheme will be inserted into the calling
    module's globals and prefixed with `PHAC_ASPC_` when fetching the
    environment variable.

    prefix can be used to change the environment variable prefix that is added
    to the beginning on the variables defined in conf.  By default this value is
    `PHAC_ASPC_`.

    conf is a dictionary used to generate the scheme for django-environ.
    """

    mod = inspect.getmodule(inspect.stack()[1][0])
    env = get_env(prefix, **conf)

    for name in conf:
        setattr(mod, name, get_env_value(env, name))
