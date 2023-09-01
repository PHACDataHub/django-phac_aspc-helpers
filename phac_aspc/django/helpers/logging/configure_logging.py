import logging.config
import os
import sys

import structlog

from phac_aspc.django.settings.utils import is_running_tests

DATE_FORMAT = "%d/%b/%Y %H:%M:%S"

STRUCTLOG_PRE_PROCESSORS = (
    structlog.contextvars.merge_contextvars,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.CallsiteParameterAdder(
        {
            structlog.processors.CallsiteParameter.FUNC_NAME,
            structlog.processors.CallsiteParameter.LINENO,
        }
    ),
    structlog.processors.UnicodeDecoder(),
)

_default_suffix = "phac_helper_"

# Exposed so that consumer's can add new handlers that use these formatters
PHAC_HELPER_CONSOLE_FORMATTER_KEY = f"{_default_suffix}console_formatter"
PHAC_HELPER_JSON_FORMATTER_KEY = f"{_default_suffix}json_formatter"
PHAC_HELPER_PLAINTEXT_FORMATTER_KEY = f"{_default_suffix}plaintext_formatter"


def configure_logging(
    lowest_level_to_log="INFO",
    format_console_logs_as_json=True,
    additional_handlers=None,
    additional_formatter_key_structlog_renderer_pairs=None,
):
    # From https://www.structlog.org/en/stable/standard-library.html#rendering-within-structlog
    # Effectively makes structlog a wrapper for the sandard library `logging` module, which makes
    # our following `logging` configuration the single source of truth on project logging, and means
    # `logging.getLogger()` and `structlog.get_logger()` produce consistent output (which is very
    # nice to have when packages might be logging via either)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *STRUCTLOG_PRE_PROCESSORS,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        # `wrapper_class` is the bound logger that you get back from
        # get_logger(). This one imitates the API of `logging.Logger`.
        wrapper_class=structlog.stdlib.BoundLogger,
        # `logger_factory` is used to create wrapped loggers that are used for
        # OUTPUT. This one returns a `logging.Logger`. The final value (a JSON
        # string) from the final processor (`JSONRenderer`) will be passed to
        # the method of the same name as that you've called on the bound logger.
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Effectively freeze configuration after creating the first bound logger
        cache_logger_on_first_use=True,
    )

    formatters = {
        PHAC_HELPER_CONSOLE_FORMATTER_KEY: renderer_to_formatter(
            structlog.dev.ConsoleRenderer()
        ),
        PHAC_HELPER_JSON_FORMATTER_KEY: renderer_to_formatter(
            structlog.processors.JSONRenderer()
        ),
        PHAC_HELPER_PLAINTEXT_FORMATTER_KEY: {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(module)s:%(lineno)s] %(message)s",
            "datefmt": DATE_FORMAT,
        },
        **{
            formatter_key: renderer_to_formatter(renderer)
            for (formatter_key, renderer) in (
                additional_formatter_key_structlog_renderer_pairs or {}
            )
        },
    }

    handlers = {
        f"{_default_suffix}console_handler": {
            "class": "logging.StreamHandler",
            "level": lowest_level_to_log,
            "stream": (
                # Muting console logging output when running tests, because it makes
                # pytests own console output harder to follow (and pytest captures and
                # reports errors after all tests have finished running anyway)
                # pylint: disable=consider-using-with
                open(os.devnull, "w", encoding="UTF-8")
                if is_running_tests()
                else sys.stdout
            ),
            "formatter": (
                PHAC_HELPER_JSON_FORMATTER_KEY
                if format_console_logs_as_json
                else PHAC_HELPER_CONSOLE_FORMATTER_KEY
            ),
        },
        **(additional_handlers or {}),
    }

    # Configure the standard library logging module
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": handlers,
            "root": {
                "level": lowest_level_to_log,
                "handlers": list(handlers.keys()),
            },
        }
    )

    # There's a separate class of warnings (e.g. warning.warn) that, by default, are handled
    # outside the logging system (even though logging has its own WARNING category). They can
    # be configured to surface as warning-level logs. No reason not to!
    logging.captureWarnings(True)


def renderer_to_formatter(renderer):
    return {
        "()": structlog.stdlib.ProcessorFormatter,
        "datefmt": DATE_FORMAT,
        "foreign_pre_chain": STRUCTLOG_PRE_PROCESSORS,
        "processor": renderer,
    }
