"""Recommended values related to security controls"""
from django.conf import settings

#  AC-11 - Session controls
SESSION_COOKIE_AGE=60 # Default expiring 20 minutes
SESSION_COOKIE_SECURE=True # Use HTTPS
