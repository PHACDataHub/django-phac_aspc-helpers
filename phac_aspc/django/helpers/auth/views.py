"""OAuth authentication related views"""
from urllib import parse

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from authlib.integrations.django_client import OAuth, OAuthError

from phac_aspc.django.settings.security_env import get_oauth_env_value
from phac_aspc.django.helpers.auth.issuer_validators import ISS_VALIDATORS

oauth = OAuth()

PROVIDER = get_oauth_env_value("PROVIDER")
BACKEND = get_oauth_env_value("USE_BACKEND")
REDIRECT_LOGIN = get_oauth_env_value("REDIRECT_ON_LOGIN")
SG_DEV_APP_CLIENT_ID = get_oauth_env_value("SG_DEV_APP_CLIENT_ID")
SG_DEV_APP_CLIENT_SECRET = get_oauth_env_value("SG_DEV_APP_CLIENT_SECRET")

PROVIDER_FIELDS = {
    "microsoft": {
        "name": "name",
        "id": "oid",
    },
    "dev_secure_gateway": {
        "name": "email",
        "id": "sub",
    },
}


if PROVIDER:
    oauth.register(PROVIDER)

if SG_DEV_APP_CLIENT_ID and SG_DEV_APP_CLIENT_SECRET:
    oauth.register("dev_secure_gateway")
    

def login(request):
    """Redirect users to the provider's login page"""
    provider = request.GET.get("provider")
    if provider:
        client = oauth.create_client(provider)
        auth_url_extra_params = {"state": request.build_absolute_uri()}
        
        return client.authorize_redirect(
            request,
            request.build_absolute_uri(reverse("phac_aspc_authorize")),
            **auth_url_extra_params
        )
    raise ImproperlyConfigured("The login route is not configured.")


def authorize(request):
    """Verify the token received and perform authentication"""
    query_params = dict(
        parse.parse_qsl(parse.urlsplit(request.GET["state"]).query)
    )
    provider = query_params["provider"]
    if provider:
        try:
            client = oauth.create_client(provider)
            token = client.authorize_access_token(
                request,
                claims_options={"iss": {"essential": True, "validate": ISS_VALIDATORS[provider]}},
            )
            user_info = token["userinfo"]

            user_details = {
                "email": user_info.get("email", None)
            }
            
            fields = PROVIDER_FIELDS.get(provider)
            user_details["name"] = user_info.get(fields["name"], None)
            user_details["id"] = user_info.get(fields["id"], None)

            user = authenticate(request, user_info=user_details)
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
