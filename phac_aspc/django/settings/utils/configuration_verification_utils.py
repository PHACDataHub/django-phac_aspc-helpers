"""This file contains utilities for asserting that consuming Django apps meet the
library settings requirements.
"""

import inspect

from django.core import checks


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

    # Modules that read global state are best deffered to call time rather than module-load
    # pylint: disable=import-outside-toplevel
    from phac_aspc.django.settings.logging_env import get_logging_env_value

    prefix_list = warn_and_remove(["modeltranslation", "axes"], app_list)

    logging_app = (
        ["django_structlog"] if get_logging_env_value("USE_HELPERS_CONFIG") else []
    )

    suffix_list = warn_and_remove(
        [
            "phac_aspc.django.helpers",
            "rules.apps.AutodiscoverRulesConfig",
            *logging_app,
        ],
        app_list,
    )

    return prefix_list + app_list + suffix_list


def configure_authentication_backends(backend_list):
    """Return the authentication backend list includes those required by this
    library.

    By default importing the settings will automatically configure the backend,
    however if you want to customize the authentication backend used by your
    project, you can use this method to ensure proper configuration."""

    # Modules that read global state are best deffered to call time rather than module-load
    # pylint: disable=import-outside-toplevel
    from phac_aspc.django.settings.security_env import get_oauth_env_value

    oauth_backend = (
        [get_oauth_env_value("USE_BACKEND")]
        if get_oauth_env_value("PROVIDER") and get_oauth_env_value("USE_BACKEND")
        else []
    )

    prefix_backends = warn_and_remove(
        ["axes.backends.AxesStandaloneBackend"] + oauth_backend, backend_list
    )
    return prefix_backends + backend_list


def configure_middleware(middleware_list):
    """Return the list of middleware configured for this library"""
    # Modules that read global state are best deffered to call time rather than module-load
    # pylint: disable=import-outside-toplevel
    from phac_aspc.django.settings.logging_env import get_logging_env_value

    logging_middleware = (
        ["django_structlog.middlewares.RequestMiddleware"]
        if get_logging_env_value("USE_HELPERS_CONFIG")
        else []
    )

    prefix = warn_and_remove(
        [
            "axes.middleware.AxesMiddleware",
            "django.middleware.locale.LocaleMiddleware",
        ]
        + logging_middleware,
        middleware_list,
    )
    return prefix + middleware_list
