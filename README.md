# Django Helpers

Provides a series of helpers to provide a consistent experience across
PHAC-ASPC's Django based projects.

## Third party applications

By using this library, the following django applications will automatically be
added to your django project:

- [django-axes](https://django-axes.readthedocs.io/)
- [django-environ](https://django-environ.readthedocs.io/)
- [django-modeltranslation](https://django-modeltranslation.readthedocs.io/)

## Quick start

```bash
pip install django-phac_aspc-helpers
```

```python
# settings.py

from phac_aspc.django.settings.utils import configure_apps, configure_middleware
from phac_aspc.django.settings import *

INSTALLED_APPS = configure_apps([...])
MIDDLEWARE = configure_middleware([...])
```

> Note: Replace [...] above with the corresponding existing configuration from
> your project.

The `configure_apps` and `configure_middleware` utility functions will insert
the appropriate applications into their correct location in your project's
application and middleware lists.

```python
# urls.py

from  phac_aspc.django.helpers.urls import urlpatterns as phac_aspc_helper_urls

urlpatterns = [
    ...
    *phac_aspc_helper_urls,
]
```

> Note: Add `*phac_aspc_helper_urls` to the list or `urlpatterns` exported by
> your project's `urls` module.

### Jinja

If you are using jinja you can use django template tags by adding
them to the global environment like this:

```python
import phac_aspc.django.helpers.templatetags as phac_aspc

def environment(**options):
    env = Environment(**options)
    env.globals.update({
       "phac_aspc": phac_aspc,
    })
    return env
```

For more information, refer to the Jinja
[documentation](https://jinja.palletsprojects.com/en/3.0.x/api/).

## Environment variables

Several settings or behaviours implemented by this library can be controlled via
environment variables.  This is done via the
[django-environ](https://django-environ.readthedocs.io/en/latest/) library.
(Refer to their documentation on how to format special data types like lists)
If your project root has a `.env` file, those values will be used.

If you want to use environment variables in your project's configuration, you
can simply reference django-environ directly as it will automatically be
installed.  For example:

```python
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env()

DEBUG = env('DEBUG')

```

This library also provides a utility that automatically declares a module level
global while checking the environment.  It is particularly useful when declaring
django settings.

```python
from phac_aspc.django.settings.utils import global_from_env

global_from_env(
    SESSION_COOKIE_AGE=(int, 1200),
)
```

The example above creates the module level global `SESSION_COOKIE_AGE` with a
default value of 1200, unless there is an environment variable (or **.env** file
entry) `PHAC_ASPC_SESSION_COOKIE_AGE`.  By default the declared variable name is
prefixed with `PHAC_ASPC_`.  The prefix can be changed by providing a custom
prefix.

```python
from phac_aspc.django.settings.utils import global_from_env

global_from_env(
    prefix='MY_PREFIX_',
    SESSION_COOKIE_AGE=(int, 1200),
)
```

### Environment variable list

All variables are prefixed with `PHAC_ASPC_` to avoid name conflicts.  

| Variable                        | Type | Purpose                         |
| ------------------------------- | ---- | ------------------------------- |
| PHAC_ASPC_SESSION_COOKIE_AGE    | int  | Session expiry in seconds       |
| PHAC_ASPC_SESSION_COOKIE_SECURE | bool | Use secure cookies (HTTPS only) |
| PHAC_ASPC_LANGUAGE_CODE         | str  | Default language                |

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

#### AC-7 Automatic lockout of users after invalid login attempts

[django-axes](https://django-axes.readthedocs.io) is used to monitor and lockout
users who fail to successfully authenticate.

The default configuration makes the following configuration changes to django:

- An attempt is identified by the combination of incoming IP address and
  the username,
- Both successful logins and failures are recorded to the database,
- The django project is assumed to be behind 1 reverse proxy (SSL),
- After 3 login failures, the account is locked out for 30 minutes.

To require an administrator to unlock the account, or to alter the lockout
duration, you can modify the `AXES_COOLOFF_TIME` setting.

```python
# settings.py

# Examples of AXES_COOLOFF_TIME settings
AXES_COOLOFF_TIME = None   # An administrator must unlock the account
AXES_COOLOFF_TIME = 2      # Accounts will be locked out for 2 hours
```
For more information regarding available configuration options, visit
django-axes's [documentation](https://django-axes.readthedocs.io/en/latest/4_configuration.html)

There are also a few command line management commands available, for example to
remove all of the lockouts you can run:

```bash
python -m manage axes_reset
```
See the [usage](https://django-axes.readthedocs.io/en/latest/3_usage.html)
documentation for more details.

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

Configuration parameters can also be overridden using environment variables.
For example here is a **.env** file that achieves the same result as above.

```bash
# .env
PHAC_ASPC_SESSION_COOKIE_AGE=1800
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
