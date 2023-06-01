from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth import get_user_model, login as auth_login
from django.http.request import HttpRequest
from django.conf import settings


class PhacAspcOAuthBackend(BaseBackend):
    def _sync_user(self, user, user_info, force=False):
        if (
            not force
            or user.email != user_info["email"]
            or user.first_name != user_info["given_name"]
            or user.last_name != user_info["family_name"]
        ):
            user.email = user_info["email"]
            user.first_name = user_info["given_name"]
            user.last_name = user_info["family_name"]
            user.save()

    def authenticate(
        self, request: HttpRequest, user_info: dict | None = None, **kwargs: Any
    ) -> AbstractBaseUser | None:
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
