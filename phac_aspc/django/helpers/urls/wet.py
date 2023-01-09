"""Setup URLs for views related to WET"""
from django.urls import path

from ..views import wet

urlpatterns = [
    path("phac-aspc/helpers/session", wet.session, name="phac_aspc_helpers_session")
]
