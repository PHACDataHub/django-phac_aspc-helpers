"""Logging configuration env var configs and getters"""
from phac_aspc.django.settings.utils.env_utils import (
    get_env,
    get_env_value,
)
from phac_aspc.django.settings.utils.test_utils import is_running_tests

logging_env = get_env(
    LOGGING_USE_HELPERS_CONFIG=(bool, False),
    LOGGING_LOWEST_LEVEL=(str, "INFO"),
    LOGGING_MUTE_CONSOLE_HANDLER=(bool, is_running_tests()),
    LOGGING_FORMAT_CONSOLE_LOGS_AS_JSON=(bool, True),
    LOGGING_AZURE_INSIGHTS_CONNECTION_STRING=(str, None),
    LOGGING_SLACK_WEBHOOK_URL=(str, None),
)


def get_logging_env_value(key):
    return get_env_value(logging_env, f"LOGGING_{key}")
