"""This file contains utilities for detecting and configuring the PHAC helpers'
testing environment
"""
import sys

from django.conf import settings


def configure_settings_for_tests():
    """
    Modify django settings so they are suitable to run unit tests.
      - Disables the Axes authentcation backend, to allow the test client
        to function.  You could instead modify the request as described here:
        https://django-axes.readthedocs.io/en/latest/3_usage.html#authenticating-users
    """
    # settings.AXES_ENABLED = False
    settings.AUTHENTICATION_BACKENDS = [
        x
        for x in settings.AUTHENTICATION_BACKENDS
        if x != "axes.backends.AxesStandaloneBackend"
    ]


def is_running_tests():
    """Detect if the app process was launched by a test-runner command"""
    return "test" in sys.argv or any("pytest" in arg for arg in sys.argv)
