from phac_aspc.django.helpers.logging.configure_logging import (
    configure_structlog_and_stdlib_logging,
    PHAC_HELPER_JSON_FORMATTER_NAME,
    PHAC_HELPER_CONSOLE_HANDLER_NAME,
)
from phac_aspc.django.settings.utils import get_env, get_env_value

# `LOGGING_CONFIG = None` drops the Django default logging config rather than merging
# our rules with it. I preffer this as having to consult the default rules and work out
# what is or isn't overwritten by the merging just feels like gotcha city for future
# maintainers. This doesn't disable built-in loggers, just let's us cleanly customize
# the handlers and formatters that will be catching them
LOGGING_CONFIG = None

logging_env = get_env(
    LOGGING_LOWEST_LEVEL=(str, "INFO"),
    LOGGING_FORMAT_CONSOLE_LOGS_AS_JSON=(bool, True),
)
configure_structlog_and_stdlib_logging(
    lowest_level_to_log=get_env_value(logging_env, "LOGGING_LOWEST_LEVEL"),
    formatter_for_default_console_handler=(
        PHAC_HELPER_JSON_FORMATTER_NAME
        if get_env_value(logging_env, "LOGGING_FORMAT_CONSOLE_LOGS_AS_JSON")
        else PHAC_HELPER_CONSOLE_HANDLER_NAME
    ),
)
