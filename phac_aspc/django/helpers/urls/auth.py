"""Setup URLs for views related to authentication"""
from django.urls import path
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns

from ...helpers.auth.views import login, authorize

urlpatterns = (
    i18n_patterns(
        path("phac_aspc_helper_login", login, name="phac_aspc_helper_login"),
        path("phac_aspc_helper_authorize", authorize, name="phac_aspc_authorize"),
    )
    if getattr(settings, "PHAC_ASPC_HELPER_OAUTH_PROVIDER", False)
    else []
)
