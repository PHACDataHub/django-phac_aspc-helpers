"""This file contains utilities helpful for settings declarations"""
import os
import inspect

import environ

from django.core import checks
from django.conf import settings


def trigger_configuration_warning(msg, **kwargs):
    """Trigger a configuration error programmatically"""

    def phac_aspc_conf_warning(
        app_configs, **conf_kwargs
    ):  # pylint: disable=unused-argument
        return [checks.Warning(msg, **kwargs)]

    checks.register(phac_aspc_conf_warning)


def warn_and_remove(items, dest_list):
    """If the items intersects with dest_list, raise a configuration warning and
    remove it from the list returned to prevent errors."""
    ret = []
    context = inspect.stack()[1].function
    hint = "You should remove it from your project to ensure proper ordering."

    for item in items:
        if item in dest_list:
            trigger_configuration_warning(
                f"{item} is already defined in the provided list.",
                id=context,
                hint=hint,
            )
            hint = None
        else:
            ret.append(item)
    return ret


def configure_apps(app_list):
    """Return an application list which includes the apps required by this
    library"""

    prefix_list = warn_and_remove(["modeltranslation", "axes"], app_list)
    suffix_list = warn_and_remove(["phac_aspc.django.helpers"], app_list)

    return prefix_list + app_list + suffix_list


def configure_authentication_backends(backend_list):
    """Return the authentication backend list includes those required by this
    library.

    By default importing the settings will automatically configure the backend,
    however if you want to customize the authentication backend used by your
    project, you can use this method to ensure proper configuration."""
    oauth_backend = (
        [getattr(settings, "PHAC_ASPC_OAUTH_USE_BACKEND", "")]
        if getattr(settings, "PHAC_ASPC_OAUTH_USE_BACKEND", "")
        else []
    )

    prefix_backends = warn_and_remove(
        ["axes.backends.AxesStandaloneBackend"] + oauth_backend, backend_list
    )
    return prefix_backends + backend_list


def configure_middleware(middleware_list):
    """Return the list of middleware configured for this library"""
    prefix = warn_and_remove(
        ["axes.middleware.AxesMiddleware", "django.middleware.locale.LocaleMiddleware"],
        middleware_list,
    )
    return prefix + middleware_list


def get_env_value(env, key, prefix="PHAC_ASPC_"):
    """Return prefixed value from environment"""
    return env(f"{prefix}{key}")


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


def configure_settings_for_tests():
    """
    Modify django settings so they are suitable to run unit tests.
      - Disables the Axes authentcation backend, to allow the test client
        to function.  You could instead modify the request as described here:
        https://django-axes.readthedocs.io/en/latest/3_usage.html#authenticating-users
    """
    # settings.AXES_ENABLED = False
    settings.AUTHENTICATION_BACKENDS = [
        x
        for x in settings.AUTHENTICATION_BACKENDS
        if x != "axes.backends.AxesStandaloneBackend"
    ]
