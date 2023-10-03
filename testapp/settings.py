from glob import glob
from pathlib import Path

PHAC_ASPC_LOGGING_USE_HELPERS_CONFIG = True
# pylint: disable=wrong-import-position, wildcard-import, unused-wildcard-import
from phac_aspc.django.settings.logging import *

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "testapp",
    "phac_aspc.django.helpers",
]
USE_I18N = (True,)
LANGUAGE = (
    ("fr-ca", "French"),
    ("en-ca", "English"),
)
LANGUAGE_CODE = "en-ca"
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "testapp.User"

TEST_RUNNER = "testapp.tests.pytest_runner.PytestRunner"

context_processors = [
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": glob(
            str(Path(__file__).parent.joinpath("**/templates")),
            recursive=True,
        ),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": context_processors,
        },
    },
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": glob(
            str(Path(__file__).parent.joinpath("**/jinja2")),
            recursive=True,
        ),
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "testapp.jinja2.environment",
            "context_processors": context_processors,
        },
    },
]

STATICFILES_DIRS = glob(
    str(Path(__file__).parent.joinpath("**/static")),
    recursive=True,
)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}

SECRET_KEY = "abcdefg"
