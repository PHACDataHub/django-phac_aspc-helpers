"""This file contains utilities for accessing env values used by consuming libraries 
to configure PHAC helpers' behaviour
"""
import os
import inspect
from importlib.util import find_spec

import environ

PHAC_ENV_PREFIX = "PHAC_ASPC_"


def get_env_value(env, key, prefix=PHAC_ENV_PREFIX):
    """Returns the value for the prefixed key from the provided env, unless that
    key exists in the Django settings in which case the settings value is used
    """
    # Modules that read global state are best deffered to call time rather than module-load
    from django.conf import settings  # pylint: disable=import-outside-toplevel

    prefixed_key = f"{prefix}{key}"

    return getattr(
        settings,
        prefixed_key,
        env(prefixed_key),
    )


def find_env_file(path):
    """Traverse directories backwards starting at `path`, returns the path of the
    first .env file found, or `None` otherwise.
    """

    # look for .env file in provided path
    filename = os.path.join(path, ".env")
    if os.path.isfile(filename):
        return filename

    # when called on the root dir, os.path.dirname returns the root dir2
    parent = os.path.dirname(path)

    # recurse backwards till we reach the root
    # (doesn't sit right, but there's no non-hacky way to know where the
    # consuming repo's root is; other env packages like dotenv also
    # default to searching backwards till they hit root)
    if parent and parent != path:
        return find_env_file(parent)

    return None


def get_env(prefix=PHAC_ENV_PREFIX, **conf):
    """Return django-environ configured with the provided values and
    using the prefix.

    `prefix` can be used to change the environment variable prefix that is added
    to the beginning on the variables defined in conf. By default this value is
    `PHAC_ASPC_`.

    `conf` is a dictionary used to generate the scheme for django-environ.

    Will attempt to find and load from a .env, starting in the directory of the consuming
    application's `DJANGO_SETTINGS_MODULE` and traveling back towards root. Continues
    even if no .env is found, with every env var taking it's default from `conf`
    instead.

    See https://django-environ.readthedocs.io/en/latest/api.html#environ.Env for
    additional information on the scheme.
    """

    scheme = {}
    for name, values in conf.items():
        scheme[f"{prefix}{name}"] = values

    env = environ.Env(**scheme)

    settings_path_of_consuming_app = os.path.dirname(
        find_spec(os.getenv("DJANGO_SETTINGS_MODULE")).origin
    )
    nearest_ancestor_dot_env = find_env_file(settings_path_of_consuming_app)
    if nearest_ancestor_dot_env and os.path.isfile(nearest_ancestor_dot_env):
        environ.Env.read_env(nearest_ancestor_dot_env)

    return env


def global_from_env(prefix=PHAC_ENV_PREFIX, **conf):
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
        setattr(mod, name, get_env_value(env, name, prefix))
