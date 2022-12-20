"""Setup URLs for views related to WET"""
from django.urls import path, include, re_path

from ..views import wet

urlpatterns = [
    path('phac-aspc/helpers/session', wet.session, name='phac_aspc_helpers_session')
]
