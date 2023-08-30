from phac_aspc.django.helpers.logging.logging_utils import configure_logging
from phac_aspc.django.settings.utils import get_env, get_env_value, is_running_tests


# `LOGGING_CONFIG = None` drops the Django default logging config rather than merging
# our rules with it. I preffer this as having to consult the default rules and work out
# what is or isn't overwritten by the merging just feels like gotcha city for future
# maintainers. This doesn't disable built-in loggers, just let's us cleanly customize
# the handlers and formatters that will be catching them
LOGGING_CONFIG = None

logging_config = get_env(
    LOGGING_LOWEST_LEVEL=(str, "INFO"),
    LOGGING_FORMAT_CONSOLE_LOGS_AS_JSON=(bool, True),
    LOGGING_SLACK_WEBHOOK_URL=(str, None),
    LOGGING_SLACK_WEBHOOK_FAIL_SILENT=(bool, None),
)

slack_webhook_fail_silent = get_env_value(
    logging_config, "LOGGING_SLACK_WEBHOOK_FAIL_SILENT"
)
if (
    get_env_value(logging_config, "LOGGING_SLACK_WEBHOOK_URL") is None
    and slack_webhook_fail_silent is None
):
    slack_webhook_fail_silent = True

configure_logging(
    lowest_level_to_log=get_env_value(logging_config, "LOGGING_LOWEST_LEVEL"),
    format_console_logs_as_json=get_env_value(
        logging_config, "LOGGING_FORMAT_CONSOLE_LOGS_AS_JSON"
    ),
    slack_webhook_url=get_env_value(logging_config, "LOGGING_SLACK_WEBHOOK_URL"),
    slack_webhook_fail_silent=slack_webhook_fail_silent,
    # Mute console logging output when running tests, because it conflicts with pytests own
    # console output (which captures and reports errors after all tests have finished running)
    mute_console=is_running_tests(),
)
