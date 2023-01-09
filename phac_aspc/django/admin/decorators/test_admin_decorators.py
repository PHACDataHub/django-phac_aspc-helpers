# pylint: disable=protected-access
"""Test admin decorators"""
from django.db import models
from django.contrib.admin import site

from phac_aspc.django.helpers.ready import process_ready_hooks
from .admin_decorators import add_admin


def test_add_admin_decorator():
    """Ensure add_admin decorator works"""

    @add_admin()
    class TestModel(models.Model):
        """Example Model to be tested"""

        name = models.TextField()

    class TestOtherModel(models.Model):
        """Example Model to not be tested"""

        name = models.TextField()

    assert len(site._registry) == 0

    process_ready_hooks()

    assert len(site._registry) == 1

    assert TestModel in site._registry

    assert TestOtherModel not in site._registry
