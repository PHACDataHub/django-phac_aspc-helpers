"""Provides all URLs in a single module"""
from .wet import urlpatterns as wet_patterns
from .auth import urlpatterns as auth_patterns

urlpatterns = wet_patterns + auth_patterns

__all__ = ['urlpatterns',]
