"""From this module import * in your settings.py for a better default logging configuration"""
from phac_aspc.django.helpers.logging.configure_logging import (
    configure_uniform_std_lib_and_structlog_logging,
    _default_suffix,
    PHAC_HELPER_JSON_FORMATTER_KEY,
    PHAC_HELPER_PRETTY_JSON_FORMATTER_KEY,
    PHAC_HELPER_CONSOLE_FORMATTER_KEY,
)
from .logging_env import get_logging_env_value


if get_logging_env_value("USE_HELPERS_CONFIG"):
    # `LOGGING_CONFIG = None` drops the Django default logging config rather than merging
    # our rules with it. This is prefferable as having to consult the default rules and work out
    # what is or isn't overwritten by the merging just feels like gotcha city for future
    # maintainers. This doesn't disable built-in loggers, just let's us cleanly customize
    # the handlers and formatters that will be catching them
    LOGGING_CONFIG = None

    lowest_level_to_log = get_logging_env_value("LOWEST_LEVEL")

    additional_handler_configs = {}
    additional_filter_configs = {}

    azure_insights_connection_string = get_logging_env_value(
        "AZURE_INSIGHTS_CONNECTION_STRING"
    )
    if azure_insights_connection_string is not None:
        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler
        except (ImportError, ModuleNotFoundError) as exc:
            raise ImportError(
                "The `opencensus-ext-azure` package is required for use of PHAC helper's "
                + "Azure Insights logging. You must install this dependency your self."
            ) from exc

        additional_handler_configs[f"{_default_suffix}azure_handler"] = {
            "level": lowest_level_to_log,
            "class": f"{AzureLogHandler.__module__}.{AzureLogHandler.__name__}",
            "connection_string": azure_insights_connection_string,
            "formatter": PHAC_HELPER_JSON_FORMATTER_KEY,
        }

    slack_webhook_url = get_logging_env_value("SLACK_WEBHOOK_URL")
    if slack_webhook_url is not None:
        # pylint: disable=ungrouped-imports
        from phac_aspc.django.helpers.logging.json_post_handlers import (
            SlackWebhookHandler,
        )

        class NoisyLoggerFilter:
            def filter(self, record):
                noisy_loggers = ["django.security.DisallowedHost"]

                if record.module in noisy_loggers:
                    return 0

                return 1

        noisy_logger_key = f"{_default_suffix}slack_webhook_handler_filter"

        additional_filter_configs[noisy_logger_key] = {
            "()": NoisyLoggerFilter,
        }

        additional_handler_configs[f"{_default_suffix}slack_webhook_handler"] = {
            "level": "ERROR",
            "class": f"{SlackWebhookHandler.__module__}.{SlackWebhookHandler.__name__}",
            "url": slack_webhook_url,
            "formatter": PHAC_HELPER_PRETTY_JSON_FORMATTER_KEY,
            "filters": [noisy_logger_key],
        }

    configure_uniform_std_lib_and_structlog_logging(
        lowest_level_to_log=lowest_level_to_log,
        mute_console_handler=get_logging_env_value("MUTE_CONSOLE_HANDLER"),
        additional_handler_configs=additional_handler_configs,
        console_handler_formatter_key=(
            PHAC_HELPER_CONSOLE_FORMATTER_KEY
            if get_logging_env_value("PRETTY_FORMAT_CONSOLE_LOGS")
            else PHAC_HELPER_JSON_FORMATTER_KEY
        ),
        additional_filter_configs=additional_filter_configs,
    )
