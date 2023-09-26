"""This file contains a utility for configuring PHAC helpers settings when 
in a testing environment
"""


def configure_settings_for_tests():
    """
    Modify django settings so they are suitable to run unit tests.
      - Disables the Axes authentcation backend, to allow the test client
        to function.  You could instead modify the request as described here:
        https://django-axes.readthedocs.io/en/latest/3_usage.html#authenticating-users
    """

    # Modules that read global state are best deffered to call time rather than module-load
    from django.conf import settings  # pylint: disable=import-outside-toplevel

    # settings.AXES_ENABLED = False

    settings.AUTHENTICATION_BACKENDS = [
        x
        for x in settings.AUTHENTICATION_BACKENDS
        if x != "axes.backends.AxesStandaloneBackend"
    ]
