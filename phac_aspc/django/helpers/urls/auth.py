"""Setup URLs for views related to authentication"""
from django.urls import path
from django.conf import settings

from ...helpers.auth.views import login, authorize

urlpatterns = (
    [
        path("phac_aspc_helper_login", login, name="phac_aspc_helper_login"),
        path("authorize", authorize, name="phac_aspc_authorize"),
    ]
    if settings.PHAC_ASPC_HELPER_OAUTH_PROVIDER
    else []
)
