import logging.config
import os
import sys

import structlog

from phac_aspc.django.settings.utils import is_running_tests

DEFAULT_SHARED_STRUCTLOG_PROCESSORS = (
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
PHAC_HELPER_CONSOLE_FORMATTER_NAME = f"{_default_suffix}console_formatter"
PHAC_HELPER_JSON_FORMATTER_NAME = f"{_default_suffix}json_formatter"
PHAC_HELPER_PLAINTEXT_FORMATTER_NAME = f"{_default_suffix}plaintext_formatter"
PHAC_HELPER_CONSOLE_HANDLER_NAME = f"{_default_suffix}console_handler"


def configure_structlog_and_stdlib_logging(
    lowest_level_to_log="INFO",
    formatter_for_default_console_handler=PHAC_HELPER_JSON_FORMATTER_NAME,
    mute_default_console_handler_when_running_tests=True,
    shared_structlog_processors=DEFAULT_SHARED_STRUCTLOG_PROCESSORS,
    additional_filters=None,
    additional_formatters=None,
    additional_handlers=None,
):
    # There's a separate class of warnings (e.g. warning.warn) that, by default, are handled
    # outside the logging system (even though logging has its own WARNING category). They can
    # be configured to surface as warning-level logs, which we want
    logging.captureWarnings(True)

    # From https://www.structlog.org/en/stable/standard-library.html#rendering-within-structlog
    # Effectively makes structlog a wrapper for the sandard library `logging` module, which makes
    # our following `logging` configuration the single source of truth (processors aside) on project
    # logging, and means `logging.getLogger()` and `structlog.get_logger()` produce consistent
    # output (which is very nice to have when packages might be logging via either)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_structlog_processors,
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

    default_filters = {}

    default_formatters = {
        PHAC_HELPER_CONSOLE_FORMATTER_NAME: {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
            "foreign_pre_chain": shared_structlog_processors,
        },
        PHAC_HELPER_JSON_FORMATTER_NAME: {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": shared_structlog_processors,
        },
        PHAC_HELPER_PLAINTEXT_FORMATTER_NAME: {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(module)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    }

    default_handlers = {
        PHAC_HELPER_CONSOLE_HANDLER_NAME: {
            "class": "logging.StreamHandler",
            "level": lowest_level_to_log,
            "stream": (
                # Will generally want to mute console logging output when running tests, because
                # it makes pytests own console output harder to follow (and pytest captures and
                # reports errors after all tests have finished running anyway)
                # pylint: disable=consider-using-with
                open(os.devnull, "w", encoding="UTF-8")
                if mute_default_console_handler_when_running_tests
                and is_running_tests()
                else sys.stdout
            ),
            "formatter": formatter_for_default_console_handler,
        },
    }

    # Configure the standard library logging module
    logging.config.dictConfig(
        get_stdlib_logging_dict_config(
            lowest_level_to_log,
            filters=(
                {**default_filters, **additional_filters}
                if additional_filters
                else default_filters
            ),
            formatters=(
                {**default_formatters, **additional_formatters}
                if additional_formatters
                else default_formatters
            ),
            handlers=(
                {**default_handlers, **additional_handlers}
                if additional_handlers
                else default_handlers
            ),
        )
    )


def get_stdlib_logging_dict_config(
    lowest_level_to_log,
    filters,
    formatters,
    handlers,
):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": filters or {},
        "formatters": formatters,
        "handlers": handlers,
        "root": {
            "level": lowest_level_to_log,
            "handlers": list(handlers.keys()),
        },
    }
