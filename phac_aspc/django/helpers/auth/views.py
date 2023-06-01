from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.urls import reverse
from django.contrib.auth import login as auth_login
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from authlib.integrations.django_client import OAuth, OAuthError

oauth = OAuth()
provider = getattr(settings, "PHAC_ASPC_HELPER_OAUTH_PROVIDER", False)


if provider:
    oauth.register(provider)


def validate_iss(claims, value):
    """Validate the iss claim"""
    tenant = getattr(settings, "OAUTH_MICROSOFT_TENANT", "common")
    use_tenant = tenant if tenant != "common" else claims["tid"]
    # iss = "https://login.microsoftonline.com/{}/v2.0".format(use_tenant)
    return use_tenant in value


def login(request):
    """Redirect users to the provider's login page"""
    if provider:
        client = oauth.create_client(provider)
        print(request.build_absolute_uri(reverse("phac_aspc_authorize")))
        return client.authorize_redirect(
            request, request.build_absolute_uri(reverse("phac_aspc_authorize"))
        )
    raise ImproperlyConfigured("The login route is not configured.")


def authorize(request):
    """Verify the token received and perform authentication"""
    if provider:
        try:
            client = oauth.create_client(provider)
            token = client.authorize_access_token(
                request,
                claims_options={"iss": {"essential": True, "validate": validate_iss}},
            )
            user_info = token["userinfo"]
            user = authenticate(request, user_info=user_info)
            if user is not None:
                auth_login(
                    request,
                    user=user,
                    backend="phac_aspc.django.helpers.auth.backend.PhacAspcOAuthBackend",
                )
                return HttpResponseRedirect(reverse("my_threats"))
            else:
                return HttpResponseRedirect(reverse("landing"))

        except OAuthError as err:
            return render(
                request,
                "phac_aspc/helpers/auth/error.html",
                {
                    "title": "Authentication Error",
                    "error": err.error,
                    "description": err.description,
                },
            )
        except Exception as err:
            # TODO: this should be logged.
            return render(
                request,
                "phac_aspc/helpers/auth/error.html",
                {
                    "title": "Application Error",
                    "error": "exception",
                    "description": str(err),
                },
            )
    raise ImproperlyConfigured("The authorize route is not configured.")
