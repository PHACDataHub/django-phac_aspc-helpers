"""Configuration API for the PHAC helpers logging configuration"""
import json
import logging.config
import os
import sys
from typing import Dict, Callable, Any, Literal

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

PHAC_HELPER_CONSOLE_FORMATTER_KEY = f"{_default_suffix}console_formatter"
PHAC_HELPER_PLAIN_STRING_FORMATTER_KEY = f"{_default_suffix}plaintext_formatter"
PHAC_HELPER_JSON_FORMATTER_KEY = f"{_default_suffix}json_formatter"
PHAC_HELPER_PRETTY_JSON_FORMATTER_KEY = f"{_default_suffix}pretty_json_formatter"

PHAC_HELPER_CONSOLE_HANDLER_KEY = f"{_default_suffix}console_handler"

PHAC_HELPER_NO_PASS_FILTER_KEY = f"{_default_suffix}no_pass_filter"

# flag set to true when configuration function called
is_phac_helper_logging_configuration_being_used = False


def configure_uniform_std_lib_and_structlog_logging(
    lowest_level_to_log: Literal[
        "NOTSET", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"
    ] = "INFO",
    mute_console_handler: bool = is_running_tests(),
    console_handler_formatter_key: str = PHAC_HELPER_JSON_FORMATTER_KEY,
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
            str,
        ],
    ] = None,
    additional_filter_configs: Dict[
        str,
        Dict[
            str,
            Any,
        ],
    ] = None,
):
    """Configures both structlog and the standard library logging module, enforcing
    uniform logging behaviour between the two. Log handler and formatters are shared
    between the two, and the same set of structlog processors is run on all logs.

    The baseline configuration provides a console (stdout) handler and formatters for
    basic JSON string formatting, pretty JSON string formatting, console formatting
    (with coloured text etc.), and plain text formatting. The keys for these default
    formatters are exposed as PHAC_HELPER_..._FORMATTER_KEY variables in this module.

    `additional_handler_configs` takes standard logging dict config handler definitions.

    `additional_formatter_functions` takes a dict of callables by (unique) formatter key. These
    callables are used as structlog "renderer" (end-of-chain) processors, for seralizing the
    structlog event-dict object in to a string for the handlers to emit. I recommend directly using,
    or wrapping/subclassing, existing structlog renderers here.

    `additional_filter_configs` takes standard logging dict config filter definitions.
    In Python 3.11 and above, you can instead directly provide filter functions/instances in your
    handler configs. In prior versions, you configure them separetly and reference them by key
    in your handler configs.

    Note: by default, the built in console handler is muted running tests, because it makes
    pytest's own console output harder to follow (and pytest captures and reports errors
    after all tests have finished running anyway). You can over ride this behaviour by
    explicitly passing a `mute_console_handler` value.
    """
    # Structlog configuration to effectively make it a wrapper for the sandard library `logging`
    # module, which makes our following `logging` configuration the single source of truth on
    # project logging, and means `logging.getLogger()` and `structlog.get_logger()` produce
    # consistent output (which is very nice to have when packages might be logging via either). See:
    # https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging
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
        cache_logger_on_first_use=True,
    )

    class NoPassFilter:
        def filter(self, *args, **kwargs):
            return 0

    filters = {
        PHAC_HELPER_NO_PASS_FILTER_KEY: {"()": NoPassFilter},
        **(additional_filter_configs or {}),
    }

    formatter_functions = {
        PHAC_HELPER_CONSOLE_FORMATTER_KEY: structlog.dev.ConsoleRenderer(),
        PHAC_HELPER_JSON_FORMATTER_KEY: structlog.processors.JSONRenderer(),
        PHAC_HELPER_PRETTY_JSON_FORMATTER_KEY: structlog.processors.JSONRenderer(
            # JSON string with indents, sorting, and newlines inside values preserved
            serializer=lambda *args, **kwargs: json.dumps(
                *args, indent=4, sort_keys=True, **kwargs
            ).replace("\\n", "\n")
        ),
        PHAC_HELPER_PLAIN_STRING_FORMATTER_KEY: structlog.processors.LogfmtRenderer(
            sort_keys=True
        ),
        **(additional_formatter_functions or {}),
    }

    def formatter_function_to_formatter_config(formatter_function):
        return {
            "()": structlog.stdlib.ProcessorFormatter,
            "foreign_pre_chain": STRUCTLOG_PRE_PROCESSORS,
            "datefmt": DATE_FORMAT,
            "processor": formatter_function,
        }

    formatters = {
        formatter_key: formatter_function_to_formatter_config(formatter_function)
        for (formatter_key, formatter_function) in formatter_functions.items()
    }

    handlers = {
        PHAC_HELPER_CONSOLE_HANDLER_KEY: {
            "class": "logging.StreamHandler",
            "level": lowest_level_to_log,
            "stream": (
                # pylint: disable=consider-using-with
                open(os.devnull, "w", encoding="UTF-8")
                if mute_console_handler
                else sys.stdout
            ),
            "formatter": console_handler_formatter_key,
        },
        **(additional_handler_configs or {}),
    }

    # Configure the standard library logging module
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "filters": filters,
            "formatters": formatters,
            "handlers": handlers,
            "django.request": {
                # built in django.request logging is redundant to the django_structlog
                # request middleware, filter them out to avoid messy duplicate logs
                "filter": PHAC_HELPER_NO_PASS_FILTER_KEY
            },
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

    global is_phac_helper_logging_configuration_being_used  # pylint: disable=global-statement
    is_phac_helper_logging_configuration_being_used = True
