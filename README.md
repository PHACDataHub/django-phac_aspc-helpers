# Django Helpers

Provides a series of helpers to provide a consistent experience across
PHAC-ASPC's Django based projects.

## Quick start

```bash
pip install django-phac_aspc-helpers
```

Start by adding `phac_aspc.django.helpers` to your `INSTALLED_APPS`
setting like this:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'phac_aspc.django.helpers',
]
```

> Note: The `phac_aspc.django.helpers` must appear *after* any
> application that will be using it.  Consider placing it as the
> last application in the list.

To use all recommended default settings, add this line to your project's
settings file:

```python
#settings.py
from phac_aspc.django.settings import *
```

There are also a number of views available that provide additional functionality
for things like renewing sessions.  Add them to your project's configuration.

```python

# urls.py
from  phac_aspc.django.helpers.urls import urlpatterns as phac_aspc_helper_urls

urlpatterns = [
    ...
    *phac_aspc_helper_urls,
]
```

> ## Jinja
>
> If you are using jinja you can use django template tags by adding
> them to the global environment like this:
>
> ```python
> import phac_aspc.django.helpers.templatetags as phac_aspc
>
> def environment(**options):
>    env = Environment(**options)
>    env.globals.update({
>       "phac_aspc": phac_aspc,
>    })
>    return env
> ```
>
> For more information, refer to the Jinja
> [documentation](https://jinja.palletsprojects.com/en/3.0.x/api/).


## Features

### Web Experience Toolkit (WET)

The Web Experience Toolkit is bundled with the helpers, and can easily be added
to your templates.

Your base template should be modified to:

- Specify the current language in the lang attribute of the HTML element
- Include the WET CSS files inside the HEAD element
- Include the WET script files at the end of your BODY element

A minimum base template may look like this:

```django
{% load phac_aspc_wet %}
{% load phac_aspc_localization %}
<html lang="{% phac_aspc_localization_lang %}">
    <head>
        {% phac_aspc_wet_css %}
    </head>
    <body>
        <h1>Minimum base template</h1>
        {% block content %}{% endblock %}
        {% phac_aspc_wet_scripts %}
    </body>
</html>
```

or if you're using Jinja:

```jinja
<html lang="{{ phac_aspc.phac_aspc_localization_lang() }}">
    <head>
        {{ phac_aspc.phac_aspc_wet_css() }}
    </head>
    <body>
        <h1>Minimum base template</h1>
        {% block content %}{% endblock %}
        {{ phac_aspc.phac_aspc_wet_scripts() }}
    </body>
</html>
```

#### Bundled releases

| Product                      | Version   |
| ---------------------------- | --------- |
| Web Experience Toolkit (WET) | v4.0.56.4 |
| Canada.ca (GCWeb)            | v12.5.0   |

### Security Controls

#### AC-11 Session Timeouts

The default configuration makes the following configuration changes to django:

- Sessions timeout in 20 minutes,
- Sessions cookies are marked as secure,
- Sessions cookies are discarded when the browser is closed,
- Any requests to the server automatically extends the session.

You can override any of these settings by adding them below the settings import
line.  For example to use 30 minutes sessions:

```python
#settings.py

from phac_aspc.django.settings import *

SESSION_COOKIE_AGE=1800

```

> For more information on sessions, refer to Django's
> [documentation](https://docs.djangoproject.com/en/dev/ref/settings/#sessions)

Additionally the Session Timeout UI control is available to warn users their
session is about to expire, and provide mechanisms to automatically renew the
session by clicking anywhere on the page, or by clicking on the "extend session"
button when less than 3 minutes remain.

To use it, make sure your base template has WET setup as described
[above](#web-experience-toolkit-wet), and add the following line somewhere in
your body tag.

```django
{% phac_aspc_wet_session_timeout_dialog 'logout' %}
```

or if you're using Jinja

```jinja
{{ phac_aspc.phac_aspc_wet_session_timeout_dialog(
    dict(request=request),
    'logout'
   )
}}
```

> Make sure the above is included on every page where a user can be signed in,
> preferably in the base template for the entire site.
>
> For more information on session timeout, visit the
> [documentation](https://wet-boew.github.io/wet-boew/docs/ref/session-timeout/session-timeout-en.html).

### Localization

Django will be configured to support English (en-ca) and French (fr-ca).  This
can be changed in your projects settings using `LANGUAGES` and `LANGUAGE_CODE`.

> For more information on Django's localization, see their
> [documentation](https://docs.djangoproject.com/en/4.1/topics/i18n/).

#### lang template tag

In your templates, retrieve the current language code using the `lang` tag.

```django
{% load localization %}
<html lang="{% lang %}">
```

Or in you're using Jinja

```jinja
<html lang="{{ phac_aspc.localization.lang() }}">
```


#### translate decorator

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

#### add_admin decorator

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
