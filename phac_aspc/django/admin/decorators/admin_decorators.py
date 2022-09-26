from django.contrib.admin import site, ModelAdmin, TabularInline

from modeltranslation.admin import TranslationAdmin

from phac_aspc.django.helpers.ready import execute_when_ready


class add_admin():
    """
    Add a model Django's administration interface.

    You can add a list of inlines models using the `inlines` property,
    or any other option supported by `ModelAdmin` via the `admin_options`
    property.

    Usage:
        >>> from django.db import models
        >>> from phac_aspc.django.admin.decorators import add_admin
        >>> 
        >>> @add_admin()
        >>> class Person(models.Model):
        >>>     ...
        >>>     

    """

    def __init__(self, inlines=None, admin_options=None):
        self.ao = admin_options
        self.inlines = inlines

    def __call__(self, cls):
        def register_model():
            opts = self.ao or {}
            opts["inlines"] = []
            if self.inlines is not None:
                for model in self.inlines:
                    opts["inlines"].append(type('f"{cls.__name__}_{model}InlineAdmin"',
                                                (TabularInline,), {'model': model}))
            
            base_class = TranslationAdmin if hasattr(cls, '__is_translated_model__') else ModelAdmin

            site.register(
                cls, type('f"{cls.__name__}Admin"', (base_class,), opts))
        execute_when_ready(register_model)
        return cls
