"""OAuth authentication related views"""
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
backend = getattr(settings, "PHAC_ASPC_OAUTH_USE_BACKEND", False)
redirect_login = getattr(settings, "PHAC_ASPC_OAUTH_REDIRECT_ON_LOGIN", "")

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
                    backend=backend,
                )
                return HttpResponseRedirect(
                    reverse(redirect_login) if redirect_login else "/"
                )
            else:
                return render(
                    request,
                    "phac_aspc/helpers/auth/error.html",
                    {
                        "type": "oauth",
                        "details": "Access denied",
                    },
                )

        except OAuthError as err:
            return render(
                request,
                "phac_aspc/helpers/auth/error.html",
                {
                    "type": "oauth",
                    "details": err.description,
                },
            )
        except Exception as err:  # pylint: disable=broad-exception-caught
            return render(
                request,
                "phac_aspc/helpers/auth/error.html",
                {
                    "type": "general",
                    "details": str(err),
                },
            )
    raise ImproperlyConfigured("The authorize route is not configured.")
