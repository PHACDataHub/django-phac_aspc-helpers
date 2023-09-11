"""Utilities for use alongside the PHAC helpers logging configuration"""
from typing import Dict, Any

from django.core.exceptions import MiddlewareNotUsed, ImproperlyConfigured

import structlog


def add_fields_to_all_logs_for_current_request(context_dict: Dict[str, Any]):
    """Binds structlog contextvars to all subsequent logs for the request currently being processed.

    Requires use of the PHAC helper's logging configuration and the django_structlog
    RequestMiddleware. The PHAC helper's logging configuration ensures these context
    vars are rendered when logging, and the django_structlog RequestMiddleware handles
    clearing the structlog contextvars between requests.
    """
    # fairly trivial implementation, but that's only a side effect of our logging
    # configuration, and use of django_structlog.middlewares.RequestMiddleware
    # Wrapping in a function so I can document this, and write tests against it

    # First, and more straightforward, binding structlog context vars adds to _all_
    # log output because both our `logging` and `structlog` configs share the
    # `structlog.contextvars.merge_contextvars` processor

    # Second, and more obscurely, these bound context vars only apply to the
    # _current_ request because django_structlog.middlewares.RequestMiddleware clears
    # all context vars at the end of its own response logging handler. Not well documented,
    # but expected to be stable. Clearing context vars either on new request or when finished
    # a response is recommended by structlog's own docs, and is the responsibility of any
    # framework-specific structlog wrapper
    # https://www.structlog.org/en/stable/contextvars.html#context-variables
    # https://github.com/jrobichaud/django-structlog/blob/89fdc7d8adb3cb91848f3b2856e01e5d49649d67/django_structlog/middlewares/request.py#L51

    # Modules that read global state are best deffered to call time rather than module-load
    from django.conf import settings  # pylint: disable=import-outside-toplevel

    # pylint: disable=import-outside-toplevel
    from phac_aspc.django.helpers.logging.configure_logging import (
        is_phac_helper_logging_configuration_being_used,
    )

    if "django_structlog.middlewares.RequestMiddleware" not in settings.MIDDLEWARE:
        raise MiddlewareNotUsed(
            "django_structlog.middlewares.RequestMiddleware is required for this utility"
        )

    if not is_phac_helper_logging_configuration_being_used:
        raise ImproperlyConfigured(
            "The PHAC helper's logging configuration is required for this utility"
        )

    structlog.contextvars.bind_contextvars(**context_dict)
