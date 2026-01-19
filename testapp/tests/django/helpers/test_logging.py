import json
import logging
import os
from copy import deepcopy
from unittest.mock import Mock

from django.http import HttpResponse
from django.urls import path, reverse
from django.views import View

import pytest
import responses
import structlog
from testfixtures import LogCapture

from phac_aspc.django.helpers.logging.configure_logging import (
    PHAC_HELPER_CONSOLE_HANDLER_KEY,
    PHAC_HELPER_JSON_FORMATTER_KEY,
    configure_uniform_std_lib_and_structlog_logging,
)
from phac_aspc.django.helpers.logging.json_post_handlers import (
    AbstractJSONPostHandler,
    SlackWebhookHandler,
)
from phac_aspc.django.helpers.logging.utils import (
    add_fields_to_all_logs_for_current_request,
)


@pytest.fixture(autouse=True)
def reset_logging_configs_after_test():
    # approach based on the strategy used by testfixtures's `LogCapture` class

    root_logger = logging.getLogger()

    pre_test_logger_dict = deepcopy(root_logger.manager.loggerDict)

    logger_config_keys = [
        "level",
        "filters",
        "handlers",
        "disabled",
        "propagate",
    ]
    pre_test_root_logger_config = {
        key: getattr(root_logger, key) for key in logger_config_keys
    }

    pre_test_structlog_config = structlog.get_config()

    yield

    root_logger.manager.loggerDict = pre_test_logger_dict

    for key, value in pre_test_root_logger_config.items():
        if key == "level":
            root_logger.setLevel(value)
        else:
            setattr(root_logger, key, value)

    structlog.configure(**pre_test_structlog_config)


def get_configured_logging_handler_by_name(name):
    handler = next(
        handler for handler in logging.root.handlers if handler.name == name
    )

    if not handler:
        raise ValueError(
            f'No handler with name "{name}" found on current root logger'
        )

    return handler


class CapturingHandlerWrapper(object):
    def __init__(self, handler_instance):
        self.__dict__["__class__"] = handler_instance.__class__
        self.__dict__["_wrapped_handler"] = handler_instance
        self.__dict__["name"] = f"capturing_wrapped_{handler_instance.name}"
        self.__dict__["captured_formatted_logs"] = list()

    def handle(self, record):
        record_was_emitted = self._wrapped_handler.handle(record)

        if record_was_emitted:
            self.captured_formatted_logs.append(
                self._wrapped_handler.format(record)
            )

        return record_was_emitted

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self.__dict__, attr)
        else:
            return getattr(self.__dict__["_wrapped_handler"], attr)

    def __setattr__(self, attr, value):
        setattr(self.__dict__["_wrapped_handler"], attr, value)


# loggers cache by name in some places, avoid that by incrementing ids used
_logger_factory_id_incrementor = 0


def formatted_log_capturing_logger_factory(handler=None):
    # setting default at call time rather than in the function def as the logging
    # config global mutates during tests
    if handler is None:
        handler = logging.root.handlers[0]

    # pylint: disable=global-statement
    global _logger_factory_id_incrementor

    loggers = (
        logging.getLogger(f"test_logger_{_logger_factory_id_incrementor}"),
        structlog.getLogger(
            f"test_structlogger_{_logger_factory_id_incrementor}"
        ),
    )
    _logger_factory_id_incrementor += 1

    capturing_handler = CapturingHandlerWrapper(handler)

    for logger in loggers:
        logger.addHandler(capturing_handler)

        # dropping logger level to DEBUG to make sure logs of any level
        # are handled and captured
        logger.setLevel(logging.DEBUG)

    return (*loggers, capturing_handler.captured_formatted_logs)


# `capture_all_log_records` serves a different, sometimes complementary, purpose to
# `formatted_log_capturing_logger_factory`. `capture_all_log_records` over-rides
# the configuration of the root level logger, meaning it can see and capture the log
# records from ALL logging calls, but it also clobers the root level's configured
# formatter, handler, filter, etc while in use. Use it to assert the existence of,
# and inspect, log record values from any logging source. Use the capturing logger
# factory to assert things about the formatted output of specific logging handler
# + formatter configurations
@pytest.fixture()
def capture_all_log_records():
    capture = LogCapture()
    yield capture
    capture.uninstall()


TEST_URL = "http://testing.notarealtld"


def test_configured_logging_respects_lowest_level_to_log():
    configure_uniform_std_lib_and_structlog_logging(
        console_handler_formatter_key=PHAC_HELPER_JSON_FORMATTER_KEY,
        lowest_level_to_log="WARN",
    )
    json_console_handler = get_configured_logging_handler_by_name(
        PHAC_HELPER_CONSOLE_HANDLER_KEY
    )

    (
        logger,
        structlogger,
        captured_formatted_logs,
    ) = formatted_log_capturing_logger_factory(json_console_handler)

    below_warning_level_message = "this should NOT be captured"
    above_warning_level_message = "this SHOULD be captured"

    logger.debug(below_warning_level_message)
    structlogger.debug(below_warning_level_message)

    logger.error(above_warning_level_message)
    logger.error(above_warning_level_message)

    assert len(captured_formatted_logs) == 2
    for log in captured_formatted_logs:
        assert above_warning_level_message in log


def test_configured_console_handler_formatter_is_used():
    custom_formatter_key = "custom_formatter"
    custom_formatter_func = Mock(return_value="foo")

    configure_uniform_std_lib_and_structlog_logging(
        console_handler_formatter_key=custom_formatter_key,
        additional_formatter_functions={
            custom_formatter_key: custom_formatter_func
        },
    )

    logger = logging.getLogger(
        "logger_test_configured_console_handler_formatter_is_used"
    )
    structlogger = structlog.getLogger(
        "structlogger_test_configured_console_handler_formatter_is_used"
    )

    test_log_message = "arbitrary log message"

    logger.error(test_log_message)
    assert custom_formatter_func.assert_called_once

    custom_formatter_func.reset_mock()

    structlogger.error(test_log_message)
    assert custom_formatter_func.assert_called_once


def test_configured_additional_handlers_are_used():
    custom_handler_with_custom_formatter_key = (
        "custom_handler_with_custom_formatter"
    )

    custom_formatter_key = "custom_formatter"
    custom_formatter_func = Mock(return_value="foo")

    custom_filter_key = "custom_filter"
    custom_filter_func = Mock(return_value="1")

    class CustomFilterClass:
        def filter(self, *args, **kwargs):
            return custom_filter_func()

    configure_uniform_std_lib_and_structlog_logging(
        console_handler_formatter_key=PHAC_HELPER_JSON_FORMATTER_KEY,
        additional_handler_configs={
            custom_handler_with_custom_formatter_key: {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "stream": (
                    # pylint: disable=consider-using-with
                    open(os.devnull, "w", encoding="UTF-8")
                ),
                "formatter": custom_formatter_key,
                "filters": [custom_filter_key],
            },
        },
        additional_formatter_functions={
            custom_formatter_key: custom_formatter_func
        },
        additional_filter_configs={
            custom_filter_key: {"()": CustomFilterClass}
        },
    )

    logger = logging.getLogger(
        "logger_test_configured_additional_handlers_are_used"
    )
    structlogger = structlog.getLogger(
        "structlogger_test_configured_additional_handlers_are_used"
    )

    test_log_message = "arbitrary log message"

    logger.error(test_log_message)
    custom_formatter_func.assert_called_once()
    custom_filter_func.assert_called_once()

    custom_formatter_func.reset_mock()
    custom_filter_func.reset_mock()

    structlogger.error(test_log_message)
    custom_formatter_func.assert_called_once()
    custom_filter_func.assert_called_once()


def test_configured_json_logging_consistent_between_standard_logger_and_structlogger():
    configure_uniform_std_lib_and_structlog_logging(
        console_handler_formatter_key=PHAC_HELPER_JSON_FORMATTER_KEY
    )
    json_console_handler = get_configured_logging_handler_by_name(
        PHAC_HELPER_CONSOLE_HANDLER_KEY
    )

    (
        logger,
        structlogger,
        captured_formatted_logs,
    ) = formatted_log_capturing_logger_factory(json_console_handler)

    test_log_content = "Original error should be present in captured logs"

    logger.error(test_log_content)
    structlogger.error(test_log_content)

    assert len(captured_formatted_logs) == 2
    assert json.loads(captured_formatted_logs[0])["logger"] == logger.name
    assert (
        json.loads(captured_formatted_logs[1])["logger"] == structlogger.name
    )
    assert test_log_content in captured_formatted_logs[0]

    keys_to_ignore = ("logger", "lineno", "timestamp")

    def log_to_filtered_dict(json_string):
        return {
            k: v
            for k, v in json.loads(json_string).items()
            if k not in keys_to_ignore
        }

    assert log_to_filtered_dict(
        captured_formatted_logs[0]
    ) == log_to_filtered_dict(captured_formatted_logs[1])


def test_add_fields_to_all_logs_for_current_request(
    vanilla_user_client, settings
):
    configure_uniform_std_lib_and_structlog_logging(
        console_handler_formatter_key=PHAC_HELPER_JSON_FORMATTER_KEY
    )
    json_console_handler = get_configured_logging_handler_by_name(
        PHAC_HELPER_CONSOLE_HANDLER_KEY
    )

    (
        logger,
        _structlogger,
        captured_formatted_logs,
    ) = formatted_log_capturing_logger_factory(json_console_handler)

    metadata_1 = {"metadata_key_1": "metadata_value_1"}
    metadata_2 = {"metadata_key_2": "metadata_value_2"}

    event_with_metadata_1 = "event-with-metadata-1"
    event_with_metadata_1_and_2 = "event-with-metadata-1-and-2"
    event_with_no_metadata = "event-without-metadata"

    class ViewWithLoggingSideEffect(View):
        def setup(self, request, *args, **kwargs):
            super().setup(request, *args, **kwargs)

            add_fields_to_all_logs_for_current_request(metadata_1)
            logger.info(event_with_metadata_1)

        def get(self, request, *args, **kwargs):
            add_fields_to_all_logs_for_current_request(metadata_2)

            logger.info(event_with_metadata_1_and_2)

            return HttpResponse("")

    # Using a RequestFactory to send a request directly to our test view bypasses the middle ware
    # that the `add_metadata_to_all_logs_for_current_request` implementation relies on, need to
    # send the testing request through the test client. To do this, needed a good way to patch
    # `urlpatterns`. Solution: declare a module level `urlpatterns` variable, containing the view
    # with our testing behaviour, then update the test-scopped django ROOT_URLCONF setting to
    # resolve requests via this module's `urlpatterns`
    global urlpatterns  # pylint: disable=global-variable-undefined
    urlpatterns = [
        path(
            "test/",
            ViewWithLoggingSideEffect.as_view(),
            name="log_metadata_test_route",
        ),
    ]
    settings.ROOT_URLCONF = __name__

    vanilla_user_client.get(reverse("log_metadata_test_route"))

    logger.info(event_with_no_metadata)

    captured_formatted_logs_as_dicts_by_event = {
        json.loads(json_string)["event"]: json.loads(json_string)
        for json_string in captured_formatted_logs
    }

    for key_1, value_1 in metadata_1.items():
        assert (
            captured_formatted_logs_as_dicts_by_event[event_with_metadata_1][
                key_1
            ]
            == value_1
        )
        assert (
            captured_formatted_logs_as_dicts_by_event[
                event_with_metadata_1_and_2
            ][key_1]
            == value_1
        )
        assert (
            not key_1
            in captured_formatted_logs_as_dicts_by_event[
                event_with_no_metadata
            ]
        )

    for key_2, value_2 in metadata_2.items():
        assert (
            not key_2
            in captured_formatted_logs_as_dicts_by_event[event_with_metadata_1]
        )
        assert (
            captured_formatted_logs_as_dicts_by_event[
                event_with_metadata_1_and_2
            ][key_2]
            == value_2
        )
        assert (
            not key_2
            in captured_formatted_logs_as_dicts_by_event[
                event_with_no_metadata
            ]
        )


# using the responses library is annoyingly surfacing the implementation detail that we
# currently use the requests library under the hood here, ugh.
# TODO Switch to httpretty, as a generic equivalent, once it has 3.10 support
@responses.activate
# short timeout as safety against a potential regression where the handler may try to
# handle it's _own_ exceptions/log calls, which would result in an ugly loop
@pytest.mark.timeout(3)
def test_json_post_handler_posts_json_containing_logged_text_to_provided_url():
    # can't test properties of AbstractJSONPostHandler directly, need to do so via an
    # implementing class; asserting this relationship as a pre-requisite
    assert issubclass(SlackWebhookHandler, AbstractJSONPostHandler)

    error_message = "just some arbitrary text to expect shows up somewhere in the POSTed JSON"

    def expected_request_matcher(request):
        is_json = request.headers["Content-Type"] == "application/json"
        contains_original_message = (
            not request.body.decode().find(error_message) == -1
        )

        if is_json and contains_original_message:
            return True, ""
        else:
            return (
                False,
                "Either not JSON or does not contain the original error log text",
            )

    # Will only catch calls that have JSON bodies that, somewhere, include the
    # original error message text. Make those appear to succeed (return 200)
    expected_endpoint = responses.post(
        TEST_URL,
        match=[expected_request_matcher],
        status=200,
    )

    # Will catch any calls that miss the expected endpoint, i.e. if the request
    # doesn't have a JSON body containing the logged message
    unexpected_endpoint = responses.post(TEST_URL)

    slack_handler = SlackWebhookHandler(url=TEST_URL, fail_silent=False)

    (
        logger,
        _structlogger,
        _captured_formatted_logs,
    ) = formatted_log_capturing_logger_factory(slack_handler)

    logger.error(error_message)

    assert expected_endpoint.call_count == 1
    assert unexpected_endpoint.call_count == 0


@responses.activate
@pytest.mark.timeout(3)
def test_json_post_handler_logs_own_errors_without_trying_to_rehandle_them(
    capture_all_log_records,
):
    assert issubclass(SlackWebhookHandler, AbstractJSONPostHandler)

    failing_endpoint = responses.post(TEST_URL, status=500)
    slack_handler = SlackWebhookHandler(url=TEST_URL, fail_silent=False)

    (
        logger,
        _structlogger,
        _captured_formatted_logs,
    ) = formatted_log_capturing_logger_factory(slack_handler)

    message = "Original error"
    logger.error(message)

    # only attempted to POST once
    assert failing_endpoint.call_count == 1

    # original error log was seen by the root logger
    capture_all_log_records.check_present(
        (
            logger.name,
            "ERROR",
            message,
        )
    )

    # ... as well as some additional error log from the SlackWebhookHandler module
    # itself, from the post request returning a 500
    assert (
        len(
            list(
                filter(
                    lambda record: SlackWebhookHandler.__module__
                    not in record.name,
                    capture_all_log_records.records,
                )
            )
        )
        > 0
    )


@responses.activate
@pytest.mark.timeout(3)
def test_json_post_handler_emits_no_error_logs_in_fail_silent_mode(
    capture_all_log_records,
):
    assert issubclass(SlackWebhookHandler, AbstractJSONPostHandler)

    failing_endpoint = responses.post(TEST_URL, status=500)
    slack_handler = SlackWebhookHandler(url=TEST_URL, fail_silent=True)

    (
        logger,
        _structlogger,
        _captured_formatted_logs,
    ) = formatted_log_capturing_logger_factory(slack_handler)

    message = "Original error"
    logger.error(message)

    assert failing_endpoint.call_count == 1

    capture_all_log_records.check(
        (
            logger.name,
            "ERROR",
            message,
        )
    )

    # no other logs were seen by the root logger
    assert len(capture_all_log_records.records) == 1
