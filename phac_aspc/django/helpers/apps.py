"""
Django application entrypoint
"""
from django.apps import AppConfig


from phac_aspc.django.helpers.ready import process_ready_hooks


class HelpersConfig(AppConfig):
    """
    Django application config.  As long as this application is listed
    last in INSTALLED_APPS, the `ready` function below will be executed
    when all other applications have been loaded.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phac_aspc.django.helpers'

    def ready(self):
        process_ready_hooks()
