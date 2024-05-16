# Django Helpers

Provides a series of helpers to provide a consistent experience across
PHAC-ASPC's Django based projects.

## Third party applications

By using this library, the following django applications will automatically be
added to your django project:

- [django-axes](https://django-axes.readthedocs.io/)
- [django-environ](https://django-environ.readthedocs.io/)
- [django-modeltranslation](https://django-modeltranslation.readthedocs.io/)
- [django-structlog](https://django-structlog.readthedocs.io/en/latest/)

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

> **Note**
> Replace [...] above with the corresponding existing configuration from
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

> **Note**
> Add `*phac_aspc_helper_urls` to the list or `urlpatterns` exported by
> your project's `urls` module.

### Jinja

If you are using jinja, you can use the phac_aspc jinja utils and django
templatetags by adding them to the global environment like this:

```python
import phac_aspc.django.helpers.templatetags as phac_aspc
import phac_aspc.django.helpers.jinja_utils as include_from_dtl


def environment(**options):
    env = Environment(**options)
    env.globals.update({
       "phac_aspc": phac_aspc,
       "include_from_dtl": include_from_dtl,
    })
    return env
```

For more information, refer to the Jinja
[documentation](https://jinja.palletsprojects.com/en/3.0.x/api/).

## Environment variables

Several settings or behaviours implemented by this library can be controlled via
environment variables. By default, these environment variables are read from the
`.env` file in your project's root. This is done via the [django-environ](https://django-environ.readthedocs.io/en/latest/)
library; refer to their documentation on how to format special data types like lists.

Alternatively, these environment variables can be declared in your `settings.py`
itself. There are two important caveats when doing so:

1. `settings.py` declarations take precedence over any instances of the same
   env var in your `.env` file
2. any env vars declared in `settings.py` for this library **must** be declared
   **before** any imports from `phac_aspc` occur!
   - similarly, you should not consume`phac_aspc` modules anywhere that executes
     prior to Django's consumption of your app's settings module (e.g. in `manage.py`)
   - `phac_aspc` modules that don't, directly or indirectly, depend on these
     env vars are theoretically safe anywhere, **but** we don't currently identify
     these modules, or make promises that any given module won't start depending
     on env vars in the future

All env vars for this library are prefixed with `PHAC_ASPC_`. Available `PHAC_ASPC_`
env vars are listed under their coresponding "feature" sections below.

### global_from_env

This library also provides a utility that automatically declares an un-prefixed module
level global from a prefixed env var. It is particularly useful when declaring
django settings. The default prefix used is `PHAC_ASPC_`

```python
from phac_aspc.django.settings.utils import global_from_env

global_from_env(
    SESSION_COOKIE_AGE=(int, 1200),
)
```

The example above creates the module level global `SESSION_COOKIE_AGE` taking the
value of the env var named `PHAC_ASPC_SESSION_COOKIE_AGE`, defaulting to 1200 if no
env var is found. As with other configuration env vars for this library, the value
can either come from Django settings or from a `.env` file.

An alternative prefix can also be provided as well, to use this with other env var
name spaces.

```python
from phac_aspc.django.settings.utils import global_from_env

global_from_env(
    prefix='MY_PREFIX_',
    SESSION_COOKIE_AGE=(int, 1200),
)
```

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

#### Bundled WET releases

| Product                      | Version   |
| ---------------------------- | --------- |
| Web Experience Toolkit (WET) | v4.0.56.4 |
| Canada.ca (GCWeb)            | v12.5.0   |

### Sign in using Microsoft

By adding a few environment variables, authentication using Microsoft's
identity platform is automatically configured via the [Authlib](https://docs.authlib.org/en/latest/)
library. Setting the `PHAC_ASPC_OAUTH_PROVIDER` variable to "microsoft" enables
OAuth and adds the following new routes:

- /en-ca/phac_aspc_helper_login (`phac_aspc_helper_login`)
- /fr-ca/phac_aspc_helper_login (`phac_aspc_helper_login`)
- /en-ca/phac_aspc_helper_authorize (`phac_aspc_authorize`)
- /fr-ca/phac_aspc_helper_authorize (`phac_aspc_authorize`)

The `phac_aspc_authorize` URLs above must be added to the list of redirect URLs
in the Azure App Registration.

The login flow is triggered by redirecting the browser to the named route
`phac_aspc_helper_login`. The browser will automatically redirect the user to
Microsoft's Sign in page and after successful authentication, return the user to
the redirect route named `phac_aspc_authorize` along with a token containing
information about the user.

By default, the authentication backend will look for a user who's username is
the user's uuid from Microsoft - if not found a new user is created. To
customize this behaviour, a custom authentication backend class can be specified
via `PHAC_ASPC_OAUTH_USE_BACKEND` in `settings.py`.

After successful authentication, the user is redirected to `/`. To customize
this behaviour, set `PHAC_ASPC_OAUTH_REDIRECT_ON_LOGIN` in `settings.py` to the
name of the desired route.

Redirecting to a specific page is also supported through the `?next=<url>` query parameter. See "Template Tag" examples below.

```python

PHAC_ASPC_OAUTH_USE_BACKEND = "custom.authentication.backend"
PHAC_ASPC_OAUTH_REDIRECT_ON_LOGIN = "home"

# pylint: disable=wrong-import-position, unused-wildcard-import, wildcard-import
from phac_aspc.django.settings import *
```

> **Note**
> It is important that these settings be declared **before** the wildcard import.

Here is an example custom backend that sets the user's name to the value
provided by the identity service.

```python
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http.request import HttpRequest


class OAuthBackend(BaseBackend):
    def _get(self, user_info, value, default=""):
        return user_info[value] if value in user_info else default

    def _should_update(self, user_info, value, current):
        v = self._get(user_info, value)
        return v != "" and v != current

    def _sync_user(self, user, user_info, force=False):
        if (
            force
            or self._should_update(user_info, "email", user.email)
            or self._should_update(user_info, "name", user.first_name)
        ):
            user.email = self._get(user_info, "email", user.email)
            user.first_name = self._get(user_info, "name", user.first_name)
            user.save()

    def authenticate(
        self,
        request: HttpRequest,
        user_info: dict | None = None,
        **kwargs: Any,
    ) -> AbstractBaseUser | None:
        if user_info is not None:
            user_model = get_user_model()
            try:
                user = user_model.objects.get(username=user_info["oid"])
                self._sync_user(user, user_info)
            except user_model.DoesNotExist:
                user = user_model(username=user_info["oid"])
                self._sync_user(user, user_info, True)
            return user
        return None

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None

```

#### Sign-in with Microsoft Environment Variables

| Variable                          | Type | Purpose                                      |
| --------------------------------- | ---- | -------------------------------------------- |
| PHAC_ASPC_OAUTH_PROVIDER          | str  | Only "microsoft" is supported at the moment. |
| PHAC_ASPC_OAUTH_APP_CLIENT_ID     | str  | Client ID (from the App Registration)        |
| PHAC_ASPC_OAUTH_APP_CLIENT_SECRET | str  | Client Secret (from the App Registration)    |
| PHAC_ASPC_OAUTH_MICROSOFT_TENANT  | str  | Microsoft Tenant ID                          |

#### Template Tag

A "Sign in with Microsoft" button is available as a template tag:

```django
{% load phac_aspc_auth %}
{% phac_aspc_auth_signin_microsoft_button %}
```

To redirect to a specific page after logging in, pass the `next` query parameter through to the template tag as an argument.

e.g. with Jinja, on a login page where the URL ends with `?next=/some-protected-page/`:

```
{{ phac_aspc.phac_aspc_auth_signin_microsoft_button(request.GET.urlencode()) }}
```

#### Handling Errors

If there are any errors during the authentication flow, they are displayed to
the user via the [error.html](phac_aspc/django/helpers/templates/phac_aspc/helpers/auth/error.html)
template. The template can be extended using standard django templating by
creating a `templates/phac_aspc/helpers/auth/error.html` file in the host
project.

#### Strings and locales

Strings displayed to the user during the authentication flow are available in
Canada's both official languages. These strings can be customized by creating
templates in the host project. Here is a list of strings and templates used by
the authentication flow:

| Template                    | Context                                              |
| --------------------------- | ---------------------------------------------------- |
| error_title.html            | Error page title tag value                           |
| error_page_description.html | Description of error page (meta tag)                 |
| error_type_general.html     | Error header displayed for general exceptions        |
| error_type_oauth.html       | Error header displayed for authentication errors     |
| error_retry.html            | Text of retry link                                   |
| microsoft_logo.html         | Alt text of sign the Microsoft logo in signin button |
| signin_with_microsoft.html  | Text displayed in sign in button                     |

> **Note**
> String templates should be placed in the `templates/phac_aspc/helpers/strings`
> directory.

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
line. For example to use 30 minutes sessions:

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

##### Session Timeout Environment variables

All variables are prefixed with `PHAC_ASPC_` to avoid name conflicts.

| Variable                        | Type | Purpose                         |
| ------------------------------- | ---- | ------------------------------- |
| PHAC_ASPC_SESSION_COOKIE_AGE    | int  | Session expiry in seconds       |
| PHAC_ASPC_SESSION_COOKIE_SECURE | bool | Use secure cookies (HTTPS only) |

### Localization

Django will be configured to support English (en-ca) and French (fr-ca). This
can be changed in your projects settings using `LANGUAGES` and `LANGUAGE_CODE`.

> For more information on Django's localization, see their
> [documentation](https://docs.djangoproject.com/en/4.1/topics/i18n/).

#### Localization Environment variables

| Variable                | Type | Purpose          |
| ----------------------- | ---- | ---------------- |
| PHAC_ASPC_LANGUAGE_CODE | str  | Default language |

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
`django-modeltranslation`. The example below adds translations for the
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

#### Jinja2 and Django Template Language (DTL) cross-language-includes

We provide a Jinja2 utility function and a DTL template tag which allows each to
"include" from (render inline, using the including template's context) from one
template language to the other.

##### `include_from_dtl` Jinja2 util

Add the util to your jinja environment:

```python
import phac_aspc.django.helpers.jinja_utils as include_from_dtl


def environment(**options):
    env = Environment(**options)
    env.globals.update({
       ..., # other utils and constants
       "include_from_dtl": include_from_dtl,
    })
    return env
```

And then use it from a Jinja2 template:

```Jinja2
{{ include_from_dtl("some/dtl/template/path.html") }}
```

##### `phac_aspc_include_from_jinja` DTL template tag

To register the `phac_aspc_...` template tags, add `phac_aspc.django.helpers`
to `INSTALLED_APPS` in your `settings.py`.

You can then use the template tag in your DTL templates:

```DTL
{% load phac_aspc_include_from_jinja %}
{% phac_aspc_include_from_jinja "some/Jinja2/template/path.jinja2" %}
```

### Logging

#### Default logging configuration

A ready-to-use default logging configuration is available from `phac_aspc.django.settings.logging`,
with an environment variable based API for limited project-specific configuration. To use, just
import `*` from the module in to your `settings.py` and set `PHAC_ASPC_LOGGING_USE_HELPERS_CONFIG=true`
in either your `.env` file or `settings.py` (before the `phac_aspc` imports).

```python
#settings.py

from phac_aspc.django.settings.logging import *
# OR, along with all the other settings, via `from phac_aspc.django.settings import *`
```

For a **local dev** environment, I recommend setting `PHAC_ASPC_LOGGING_PRETTY_FORMAT_CONSOLE_LOGS=True`,
to switch from JSON string formatted logs to friendlier console log formatting (coloured text, indentation, etc).

For a **Google Cloud** environment, the default configuration of writing JSON strings to stdout is prod-ready.

For an **Azure Cloud** environment, I recommend creating an Azure Monitor resource, getting your azure insights connection
string for it, and configuring the app to log to it via the `PHAC_ASPC_LOGGING_AZURE_INSIGHTS_CONNECTION_STRING` env var.
This will enable and use a pre-configured Azure log handler, outputing logs with JSON formatted message fields.

In any production environment, you can optionally provide a Slack webhook via `PHAC_ASPC_LOGGING_SLACK_WEBHOOK_URL`.
This will send error and critical level logs to the webhook's slack channel. Note: this slack logging handler filters
out `django.security.DisallowedHost` logs, as they are a constant background noise. Other handlers still capture them.

##### Default Logging Configuration environment variables

These env vars configure the default logging configuration provided by `phac_aspc.django.settings.logging`. If you don't both
set `PHAC_ASPC_LOGGING_USE_HELPERS_CONFIG=True` and import those import those settings in your own `settings.py`, then the other
env vars here won't do anything.

| Variable                                           | Type | Purpose                                                           |
| -------------------------------------------------- | ---- | ----------------------------------------------------------------- |
| PHAC_ASPC_LOGGING_USE_HELPERS_CONFIG               | bool | set to true to use the PHAC helper provided logging configuration |
| PHAC_ASPC_LOGGING_LOWEST_LEVEL                     | str  | lowest logging level to print                                     |
| PHAC_ASPC_LOGGING_MUTE_CONSOLE_HANDLER             | bool | mutes the default console handler output                          |
| PHAC_ASPC_LOGGING_PRETTY_FORMAT_CONSOLE_LOGS       | bool | pretty format console logs (coloured text)                        |
| PHAC_ASPC_LOGGING_AZURE_INSIGHTS_CONNECTION_STRING | str  | if set, add a Azure log handler                                   |
| PHAC_ASPC_LOGGING_SLACK_WEBHOOK_URL                | str  | if set, add a Slack Webhook handler                               |

> **Note**
> these env vars are consumed only within `phac_aspc.django.settings.logging`.
> If using `configure_uniform_std_lib_and_structlog_logging` directly, these env vars
> won't do anything.

#### add_fields_to_all_logs_for_current_request

When the server is processing a request, this function adds additional key-value fields to the logging context.
Added context is will be present in subsequent logs\*. Context is cleared between requests.

\* at least, it will be in the structlog `event_dict` passed to the formatter (rendering processor). All of the
default PHAC helper formatters will serialize the context in to the final log output. Custom formatters may not.

Requires use of the PHAC helper's logging configuration and the django_structlog RequestMiddleware.
The PHAC helper's logging configuration ensures these context vars are rendered when logging,
and the django_structlog RequestMiddleware handles clearing the structlog contextvars between requests.

#### Customized logging configuration via configure_uniform_std_lib_and_structlog_logging

Deeper customization can be achieved by forgoing a `*` import from `phac_aspc.django.settings.logging`,
directly calling `phac_aspc.django.helpers.logging.configure_logging.configure_uniform_std_lib_and_structlog_logging`
in your settings.py instead. Be aware that this bypasses the `PHAC_ASPC_HELPER_LOGGING_...` env vars, which
are all only used in the `phac_aspc.django.settings.logging` module.

See the `configure_uniform_std_lib_and_structlog_logging` doc string for further details.

E.g. Muting the default console handler and using a custom file handler with a custom formatter

```python
#settings.py

import structlog

from phac_aspc.django.helpers.logging.configure_logging import (
    configure_uniform_std_lib_and_structlog_logging,
    DEFAULT_STRUCTLOG_PRE_PROCESSORS,
)

LOGGING_CONFIG = None

configure_uniform_std_lib_and_structlog_logging(
    mute_console_handler=True,
    additional_handler_configs={
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filename": "logs",
            "mode": "a",
            "encoding": "utf-8",
            "maxBytes": 500000,
            "backupCount": 4
            "formatter": "custom_formatter",
        }
    },
    additional_formatter_functions={
        "custom_formatter": (
            lambda _logging, _name, structlog_event_dict: (
                f"{structlog_event_dict.timestamp}: {structlog_event_dict.event}"
            )
        )
    }
)
```

## Contributing

### Local development

You can consume the helpers project locally by installing it in editable mode. This is useful for extracting project features into this library. In your requirements.txt, comment out the line with django-phac_aspc-helpers, and add the following line with the file path to this repo, then re-install. Make sure to first uninstall the package if it was already installed, e.g. `pip uninstall -y django-phac_aspc-helpers`

```ini
-e file:///absolute_path/to/django-phac_aspc-helpers
```

### Generating test coverage

1. `coverage run --source=. ./manage.py test`
2. `coverage html`
3. `python -m http.server 1337`
4. visit `http://localhost:1337/htmlcov/` and dig into modules to see which individual line coverage
