"""Handlers for JSON POST requests, for use alongside the PHAC helpers logging configuration"""
import logging.config
from abc import ABCMeta, abstractmethod


try:
    import requests
except (ImportError, ModuleNotFoundError) as exc:
    raise ImportError(
        "The `requests` package is required for use of the PHAC helpers JSON post"
        + "handlers. You must install this dependency your self."
    ) from exc


class AbstractJSONPostHandler(logging.Handler, metaclass=ABCMeta):
    """
    Handler for sending JSON formatted logs to an arbitrary endpoints. Subclasses must
    implement a get_json_from_record method to convert log records to match the target
    endpoint's API.

    Initialization requires a URL to post to, and also accepts an optional flag to
    control whether post attempts fail silently.

    Even if not failing silently, the handler will not try to post it's own error
    logs, to avoid potential failure loops when the target endpoint is unreachable.
    """

    def __init__(self, url: str, fail_silent: bool = False):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        self.url = url
        self.fail_silent = fail_silent

    def emit(self, record):
        is_own_error_log = record.name == self.logger.name and (
            record.levelname in ("ERROR", "CRITICAL")
        )

        if not is_own_error_log:
            try:
                response = requests.post(
                    self.url,
                    json=self.get_json_from_record(record),
                    timeout=1,
                )

                response.raise_for_status()

            except requests.RequestException as exception:
                if not self.fail_silent:
                    self.logger.error(
                        '%s\'s logging request to URL "%s" failed',
                        self.__class__.__name__,
                        self.url,
                        exc_info=exception,
                    )

    @abstractmethod
    def get_json_from_record(self, record):
        pass


class SlackWebhookHandler(AbstractJSONPostHandler):
    """Trivial Slack Webhook JSON post handler"""

    def get_json_from_record(self, record):
        return {"text": self.format(record)}
