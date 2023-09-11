"""Logging configuration env var configs and getters"""
from phac_aspc.django.settings.utils.env_utils import (
    PHAC_ENV_PREFIX,
    get_env,
    get_env_value,
)
from phac_aspc.django.settings.utils.test_utils import is_running_tests

LOGGING_ENV_PREFIX = f"{PHAC_ENV_PREFIX}LOGGING_"

logging_env = get_env(
    prefix=LOGGING_ENV_PREFIX,
    USE_HELPERS_CONFIG=(bool, False),
    LOWEST_LEVEL=(str, "INFO"),
    MUTE_CONSOLE_HANDLER=(bool, is_running_tests()),
    FORMAT_CONSOLE_LOGS_AS_JSON=(bool, True),
    AZURE_INSIGHTS_CONNECTION_STRING=(str, None),
    SLACK_WEBHOOK_URL=(str, None),
)


def get_logging_env_value(key):
    return get_env_value(logging_env, key, prefix=LOGGING_ENV_PREFIX)
