"""
Decorators used to provide internationalization
"""
from modeltranslation.translator import translator, TranslationOptions

from phac_aspc.django.helpers.ready import execute_when_ready


class translate():
    """Add localization to a model
    Usage:
        >>> from django.db import models
        >>> from phac_aspc.django.localization.decorators import translate
        >>> 
        >>> @translate('title')
        >>> class Person(models.Model):
        >>>     name = models.CharField(max_length=255)
        >>>     title = models.CharField(max_length=255)

        The ``title`` field will now support multiple languages as defined in
        ``LANGUAGES``.

        Special care should be taken when adding a translated model to Django's
        admin interface.  For convenience you can use the add_admin decorator
        provided by this package, or see
        https://django-modeltranslation.readthedocs.io/en/latest/

    """

    def __init__(self, fields):
        self.fields = fields

    def __call__(self, cls):
        def register_model():
            translator.register(cls, type(
                'f"{cls.__name__}TranslationOptions"', (TranslationOptions,), {'fields': self.fields}))
            cls.__is_translated_model__ = True
        execute_when_ready(register_model)
        return cls
