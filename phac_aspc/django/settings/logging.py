from django.conf import settings

from phac_aspc.django.helpers.logging.logging_utils import configure_logging
from phac_aspc.django.settings.utils import is_running_tests


# `LOGGING_CONFIG = None` drops the Django default logging config rather than merging
# our rules with it. I preffer this as having to consult the default rules and work out
# what is or isn't overwritten by the merging just feels like gotcha city for future
# maintainers. This doesn't disable built-in loggers, just let's us cleanly customize
# the handlers and formatters that will be catching them
LOGGING_CONFIG = None

configure_logging(
    lowest_level_to_log=getattr(settings, "PHAC_ASPC_LOGGING_LOWEST_LEVEL", "INFO"),
    format_console_logs_as_json=getattr(
        settings, "PHAC_ASPC_LOGGING_FORMAT_CONSOLE_LOGS_AS_JSON", True
    ),
    slack_webhook_url=getattr(settings, "PHAC_ASPC_LOGGING_SLACK_WEBHOOK_URL", None),
    slack_webhook_fail_silent=getattr(
        settings,
        "PHAC_ASPC_LOGGING_SLACK_WEBHOOK_FAIL_SILENT",
        # default to failing silent if webhook URL not set, failing loud otherwise
        bool(getattr(settings, "PHAC_ASPC_LOGGING_SLACK_WEBHOOK_URL", None)),
    ),
    # Mute console logging output when running tests, because it conflicts with pytests own
    # console output (which captures and reports errors after all tests have finished running)
    mute_console=is_running_tests(),
)
