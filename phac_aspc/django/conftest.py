"""Setup django for pytest tests"""

import django
from django.conf import settings

settings.configure(
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.contenttypes",
        "phac_aspc.django.helpers",
        "phac_aspc.django",
    ],
    USE_I18N=True,
    LANGUAGE=(
        ("fr-ca", "French"),
        ("en-ca", "English"),
    ),
)
django.setup()
