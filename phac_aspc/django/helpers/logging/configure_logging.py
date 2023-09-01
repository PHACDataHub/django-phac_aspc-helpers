import logging.config
import os
import sys
from typing import Dict, Callable, Any, Union, List

import structlog

from phac_aspc.django.settings.utils import is_running_tests

DEFAULT_DATE_FORMAT = "%d/%b/%Y %H:%M:%S"

DEFAULT_STRUCTLOG_PRE_PROCESSORS = (
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

PHAC_HELPER_CONSOLE_FORMATTER_KEY = f"{_default_suffix}console_formatter"
PHAC_HELPER_JSON_FORMATTER_KEY = f"{_default_suffix}json_formatter"
PHAC_HELPER_PLAIN_STRING_FORMATTER_KEY = f"{_default_suffix}plaintext_formatter"


def configure_logging(
    lowest_level_to_log: Union[
        "NOTSET", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"
    ] = "INFO",
    format_console_logs_as_json: bool = True,
    additional_handler_configs: Dict[
        str,
        Dict[
            str,
            Any,
        ],
    ] = None,
    additional_formatter_functions: Dict[
        str,
        Callable[
            [structlog.typing.WrappedLogger, str, structlog.typing.EventDict],
            str | bytes,
        ],
    ] = None,
    structlog_pre_processors: List[
        structlog.typing.Processor
    ] = DEFAULT_STRUCTLOG_PRE_PROCESSORS,
    datefmt: str = DEFAULT_DATE_FORMAT,
):
    # From https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging
    # Effectively makes structlog a wrapper for the sandard library `logging` module, which makes
    # our following `logging` configuration the single source of truth on project logging, and means
    # `logging.getLogger()` and `structlog.get_logger()` produce consistent output (which is very
    # nice to have when packages might be logging via either)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *structlog_pre_processors,
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
        cache_logger_on_first_use=True,
    )

    formatter_functions = {
        PHAC_HELPER_CONSOLE_FORMATTER_KEY: structlog.dev.ConsoleRenderer(),
        PHAC_HELPER_JSON_FORMATTER_KEY: structlog.processors.JSONRenderer(),
        PHAC_HELPER_PLAIN_STRING_FORMATTER_KEY: structlog.processors.LogfmtRenderer(),
        **(additional_formatter_functions or {}),
    }

    def formatter_function_to_formatter_config(formatter_function):
        return {
            "()": structlog.stdlib.ProcessorFormatter,
            "foreign_pre_chain": structlog_pre_processors,
            "datefmt": datefmt,
            "processor": formatter_function,
        }

    formatters = {
        formatter_key: formatter_function_to_formatter_config(formatter_function)
        for (formatter_key, formatter_function) in formatter_functions.items()
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
        **(additional_handler_configs or {}),
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
