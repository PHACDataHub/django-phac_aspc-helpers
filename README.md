# Django Helpers

Provides a series of helpers to provide a consistent experience accross 
PHAC-ASPC's Django based projects.

## Quick start

Start by adding `phac_aspc.django.helpers` to your `INSTALLED_APPS`
setting like this:

```python
INSTALLED_APPS = [
    ...
    'phac_aspc.django.helpers',
]
```

> Note: The `phac_aspc.django.helpers` must appear *after* any
> application that will be using it.  Consider placing it as the
> last application in the list.

Define the languages setting to the languages you want supported.

```python
LANGUAGES = (
    ('fr-ca', _('French')),
    ('en-ca', _('English')),
)
```

## Features

### translate decorator

Use this decorator on your models to add translations via 
`django-modeltranslation`.  The example below adds translations for the
`title` field.

```python
from django.db import models
from phac_aspc.django.localization.decorators import translate

@translate('title')
class Person(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
```

### add_admin decorator

Use this decorator on your model to quickly add it to Django's admin interface.

```python
from django.db import models
from phac_aspc.django.admin.decorators import add_admin

@add_admin()
class Person(models.Model):
    ...
```

You can also specify inline models as well as additional **ModelAdmin**
parameters via `inlines` and `admin_options` respectively.

```python
class SignalLocation(models.Model):
    signal = models.ForeignKey("Signal", on_delete=models.CASCADE)
    location = models.String()

@add_admin(
  admin_options={'filter_horizontal': ('source',)},
  inlines=[SignalLocation]
)
class Signal(models.Model):
    title = models.CharField(max_length=400)
    location = models.ManyToManyField("Location", through='SignalLocation')
```

