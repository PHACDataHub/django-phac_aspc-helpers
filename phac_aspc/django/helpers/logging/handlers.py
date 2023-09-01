import logging.config
from abc import ABCMeta, abstractmethod

import requests


class AbstractJSONPostHandler(logging.Handler, metaclass=ABCMeta):
    def __init__(self, url, fail_silent):
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
    def get_json_from_record(self, record):
        return {"text": self.format(record)}