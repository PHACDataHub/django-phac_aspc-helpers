"""OAuth authentication related views"""
from urllib import parse

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from authlib.integrations.django_client import OAuth, OAuthError

oauth = OAuth()

PROVIDER = getattr(settings, "PHAC_ASPC_HELPER_OAUTH_PROVIDER", False)
BACKEND = getattr(settings, "PHAC_ASPC_OAUTH_USE_BACKEND", False)
REDIRECT_LOGIN = getattr(settings, "PHAC_ASPC_OAUTH_REDIRECT_ON_LOGIN", "")

if PROVIDER:
    oauth.register(PROVIDER)


def validate_iss(claims, value):
    """Validate the iss claim"""
    tenant = getattr(settings, "OAUTH_MICROSOFT_TENANT", "common")
    use_tenant = tenant if tenant != "common" else claims["tid"]
    # iss = "https://login.microsoftonline.com/{}/v2.0".format(use_tenant)
    return use_tenant in value


def login(request):
    """Redirect users to the provider's login page"""
    if PROVIDER:
        client = oauth.create_client(PROVIDER)
        auth_url_extra_params = {"state": request.build_absolute_uri()}
        return client.authorize_redirect(
            request,
            request.build_absolute_uri(reverse("phac_aspc_authorize")),
            **auth_url_extra_params
        )
    raise ImproperlyConfigured("The login route is not configured.")


def authorize(request):
    """Verify the token received and perform authentication"""
    if PROVIDER:
        try:
            client = oauth.create_client(PROVIDER)
            token = client.authorize_access_token(
                request,
                claims_options={"iss": {"essential": True, "validate": validate_iss}},
            )
            user_info = token["userinfo"]
            query_params = dict(
                parse.parse_qsl(parse.urlsplit(request.GET["state"]).query)
            )
            user = authenticate(request, user_info=user_info)
            if user is not None:
                auth_login(
                    request,
                    user=user,
                    backend=BACKEND,
                )

                if "next" in query_params:
                    return HttpResponseRedirect(query_params["next"])

                return HttpResponseRedirect(
                    reverse(REDIRECT_LOGIN) if REDIRECT_LOGIN else "/"
                )
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
        except Exception as err:  # pylint: disable=broad-except
            return render(
                request,
                "phac_aspc/helpers/auth/error.html",
                {
                    "type": "general",
                    "details": str(err),
                },
            )
    raise ImproperlyConfigured("The authorize route is not configured.")
