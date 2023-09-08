"""Setup URLs for views related to authentication"""
from django.urls import path
from django.conf.urls.i18n import i18n_patterns

from phac_aspc.django.helpers.auth.views import login, authorize
from phac_aspc.django.settings.security_env import get_oauth_env_value

urlpatterns = (
    i18n_patterns(
        path("phac_aspc_helper_login", login, name="phac_aspc_helper_login"),
        path("phac_aspc_helper_authorize", authorize, name="phac_aspc_authorize"),
    )
    if get_oauth_env_value("PROVIDER")
    else []
)
