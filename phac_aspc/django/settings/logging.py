from phac_aspc.django.helpers.logging.configure_logging import (
    configure_uniform_std_lib_and_structlog_logging,
    _default_suffix,
    PHAC_HELPER_JSON_FORMATTER_KEY,
)
from phac_aspc.django.settings.utils import get_env, get_env_value

# `LOGGING_CONFIG = None` drops the Django default logging config rather than merging
# our rules with it. This is prefferable as having to consult the default rules and work out
# what is or isn't overwritten by the merging just feels like gotcha city for future
# maintainers. This doesn't disable built-in loggers, just let's us cleanly customize
# the handlers and formatters that will be catching them
LOGGING_CONFIG = None


logging_env = get_env(
    LOGGING_LOWEST_LEVEL=(str, "INFO"),
    LOGGING_FORMAT_CONSOLE_LOGS_AS_JSON=(bool, True),
    LOGGING_AZURE_INSIGHTS_CONNECTION_STRING=(str, None),
)

additional_handler_configs = {}

azure_insights_connection_string = get_env_value(
    logging_env, "LOGGING_AZURE_INSIGHTS_CONNECTION_STRING"
)
if not azure_insights_connection_string is None:
    additional_handler_configs[f"{_default_suffix}azure_handler"] = {
        "level": get_env_value(logging_env, "LOGGING_LOWEST_LEVEL"),
        "class": "opencensus.ext.azure.log_exporter.AzureLogHandler",
        "connection_string": azure_insights_connection_string,
        "formatter": PHAC_HELPER_JSON_FORMATTER_KEY,
    }

configure_uniform_std_lib_and_structlog_logging(
    lowest_level_to_log=get_env_value(logging_env, "LOGGING_LOWEST_LEVEL"),
    format_default_console_logs_as_json=get_env_value(
        logging_env, "LOGGING_FORMAT_CONSOLE_LOGS_AS_JSON"
    ),
    additional_handler_configs=additional_handler_configs,
)
