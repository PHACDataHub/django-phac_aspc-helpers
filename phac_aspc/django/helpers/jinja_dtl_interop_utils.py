from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def assert_both_dtl_and_jinja_configured():
    are_both_dtl_and_jinja_configured = map(
        lambda template_backend: next(
            filter(
                lambda template_config: template_config["BACKEND"] == template_backend,
                settings.TEMPLATES,
            ),
            False,
        ),
        [
            "django.template.backends.django.DjangoTemplates",
            "django.template.backends.jinja2.Jinja2",
        ],
    )

    if not are_both_dtl_and_jinja_configured:
        raise ImproperlyConfigured(
            "settings.TEMPLATES must include both the DjangoTemplate and Jinja2 backends"
        )

    return are_both_dtl_and_jinja_configured
