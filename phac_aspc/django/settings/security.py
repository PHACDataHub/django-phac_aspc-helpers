"""Recommended values related to security controls"""
from django.conf import settings

#  AC-11 - Session controls
SESSION_COOKIE_AGE=1200 # By default expire sessions in 20 minutes
SESSION_COOKIE_SECURE=True # Use HTTPS
SESSION_EXPIRE_AT_BROWSER_CLOSE=True # Sessions close when browser is closed
SESSION_SAVE_EVERY_REQUEST=True # Every requests extends the session
