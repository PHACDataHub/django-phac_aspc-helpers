"""Example authentication backend used by oauth login flow"""
from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser  # pylint: disable=unused-import
from django.contrib.auth import get_user_model
from django.http.request import HttpRequest


class PhacAspcOAuthBackend(BaseBackend):
    """Authentication backend that creates a user using only the oid and email"""
    def _sync_user(self, user, user_info, force=False):
        email = user_info["email"] if "email" in user_info else ""
        if force or (email not in ('', user.email)):
            user.email = email
            user.save()

    def authenticate(
        self, request: HttpRequest, user_info: "dict | None" = None, **kwargs: Any
    ) -> "AbstractBaseUser | None":
        if user_info is not None:
            user_model = get_user_model()
            try:
                user = user_model.objects.get(username=user_info["oid"])
                self._sync_user(user, user_info)
            except user_model.DoesNotExist:
                user = user_model(username=user_info["oid"])
                self._sync_user(user, user_info, True)
            return user
        return None

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
