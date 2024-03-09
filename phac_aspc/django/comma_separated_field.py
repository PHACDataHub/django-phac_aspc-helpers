# Mostly copied from https://github.com/ulule/django-separatedvaluesfield
# too many modifications to use the original code

from django.core import exceptions, validators
from django.db import models
from django.forms.fields import MultipleChoiceField
from django.utils.encoding import force_str
from django.utils.hashable import make_hashable
from django.utils.text import capfirst


class Creator:
    """
    A placeholder class that provides a way to set the attribute on the model.
    """

    def __init__(self, field):
        self.field = field

    # pylint: disable=redefined-builtin
    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = self.field.to_python(value)


class BaseSeparatedValuesField(models.Field):
    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token", ",")
        self.cast = kwargs.pop("cast", str)

        if kwargs.get("null", False):
            raise exceptions.ImproperlyConfigured(
                "null is not supported for CommaSeparatedTextField, forcing it to False "
            )

        kwargs["null"] = False

        if not kwargs.get("default", None):
            kwargs["default"] = ""

        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, *args, **kwargs):
        # super() assigns this method, we want to know
        # if the class already had a custom display method before this
        has_display_overide = hasattr(cls, f"get_{self.name}_display")
        super().contribute_to_class(cls, name, *args, **kwargs)

        setattr(cls, self.name, Creator(self))

        if self.choices and not has_display_overide:

            def get_display_value(model_instance):
                choices_dict = dict(make_hashable(self.flatchoices))
                # force_str() to coerce lazy strings.

                def get_formated_value(value):
                    return force_str(
                        choices_dict.get(make_hashable(value), value),
                        strings_only=True,
                    )

                values = getattr(model_instance, self.attname)
                pretty_values = [get_formated_value(value) for value in values if value]

                return ", ".join(pretty_values)

            setattr(cls, f"get_{self.name}_display", get_display_value)

    def validate(self, value, model_instance):
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if self.choices and value:
            choices = []

            for option_key, option_value in self.choices:
                if isinstance(option_value, (list, tuple)):
                    # This is an optgroup, so look inside the group for
                    # options.
                    for optgroup_key, _optgroup_value in option_value:
                        choices.append(optgroup_key)
                else:
                    choices.append(option_key)

            # If we have integers, convert them first to be sure we only compare
            # right types
            choices = [self.cast(choice) for choice in choices]

            for val in value:
                if val and val not in choices:
                    raise exceptions.ValidationError(
                        self.error_messages["invalid_choice"] % val
                    )

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages["null"])

        if not self.blank and value in validators.EMPTY_VALUES:
            raise exceptions.ValidationError(self.error_messages["blank"])

    def to_python(self, value):
        if not value:
            return tuple()

        values = value
        if isinstance(value, str):
            values = value.split(self.token)

        return tuple(self.cast(v) for v in values)

    def get_db_prep_value(self, value, *args, **kwargs):
        if isinstance(value, (list, tuple)):
            return self.token.join([s + "" for s in value])

        if not value:
            return value

        raise ValueError(f"Unexpected value type: {type(value)}, {value}")

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_db_prep_value(value)

    def formfield(self, *args, form_class=MultipleChoiceField, **kwargs):
        defaults = {
            "required": not self.blank,
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
        }
        if self.has_default():
            if callable(self.default):
                defaults["initial"] = self.default
                defaults["show_hidden_initial"] = True
            else:
                defaults["initial"] = self.get_default()

        if self.choices:
            defaults["choices"] = self.get_choices(include_blank=False)

            for k in list(kwargs):
                if k not in (
                    "choices",
                    "required",
                    "widget",
                    "label",
                    "initial",
                    "help_text",
                    "error_messages",
                    "show_hidden_initial",
                ):
                    del kwargs[k]
        defaults.update(kwargs)
        return form_class(**defaults)


class CommaSeparatedCharField(BaseSeparatedValuesField, models.CharField):
    pass


class CommaSeparatedTextField(BaseSeparatedValuesField, models.TextField):
    pass
