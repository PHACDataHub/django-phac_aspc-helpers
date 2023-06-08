"""Unit tests for utils.py"""
from django.core.checks.registry import registry

from .utils import (
    trigger_configuration_warning,
    warn_and_remove,
    configure_apps,
    configure_authentication_backends,
    configure_middleware,
)


def test_trigger_configuration_warning():
    """Test the trigger configuration warning successfully registers its
    check function"""
    num = len(registry.get_checks())
    msg = "this is a warning"
    trigger_configuration_warning(msg)
    assert len(registry.get_checks()) == num + 1
    assert "phac_aspc_conf_warning" in [i.__name__ for i in registry.get_checks()]
    for i in registry.get_checks():
        if i.__name__ == "phac_aspc_conf_warning":
            warn = i(None)
            assert len(warn) == 1
            assert warn[0].msg == msg


def test_warn_and_remove():
    """Test that if an item appears in the list, it is removed from the result
    and a configuration warning is called."""
    num = len(registry.get_checks())
    test = warn_and_remove(["a", "b"], ["c"])
    assert len(registry.get_checks()) == num
    assert test == ["a", "b"]

    num = len(registry.get_checks())
    test = warn_and_remove(["a", "b", "c", "d"], ["c"])
    assert len(registry.get_checks()) == num + 1
    assert test == ["a", "b", "d"]

    num = len(registry.get_checks())
    test = warn_and_remove(["a", "b", "c", "d"], ["a", "b", "c"])
    assert len(registry.get_checks()) == num + 3
    assert test == ["d"]

    num = len(registry.get_checks())
    test = warn_and_remove(["a", "b", "c", "d"], [])
    assert len(registry.get_checks()) == num
    assert test == ["a", "b", "c", "d"]

    num = len(registry.get_checks())
    test = warn_and_remove([], [])
    assert len(registry.get_checks()) == num
    assert not test

    num = len(registry.get_checks())
    test = warn_and_remove(["a", "b", "c", "d"], ["a", "b", "c", "d"])
    assert len(registry.get_checks()) == num + 4
    assert not test


def test_configure_apps():
    """Test that the configure apps utility adds the correct apps"""
    num = len(registry.get_checks())
    test = configure_apps([])
    assert test == ["modeltranslation", "axes", "phac_aspc.django.helpers"]
    assert len(registry.get_checks()) == num

    num = len(registry.get_checks())
    test = configure_apps(["a", "b"])
    assert test == ["modeltranslation", "axes", "a", "b", "phac_aspc.django.helpers"]
    assert len(registry.get_checks()) == num

    num = len(registry.get_checks())
    test = configure_apps(["a", "axes", "b"])
    assert test == ["modeltranslation", "a", "axes", "b", "phac_aspc.django.helpers"]
    assert len(registry.get_checks()) == num + 1

    num = len(registry.get_checks())
    test = configure_apps(["phac_aspc.django.helpers", "axes", "b"])
    assert test == ["modeltranslation", "phac_aspc.django.helpers", "axes", "b"]
    assert len(registry.get_checks()) == num + 2


def test_configure_authentication_backends():
    """Test that the configure_authentication_backends utility adds the correct
    backends to the list"""
    num = len(registry.get_checks())
    test = configure_authentication_backends([])
    assert test == ["axes.backends.AxesStandaloneBackend"]
    assert len(registry.get_checks()) == num

    num = len(registry.get_checks())
    test = configure_authentication_backends(["a", "b"])
    assert test == ["axes.backends.AxesStandaloneBackend", "a", "b"]
    assert len(registry.get_checks()) == num

    num = len(registry.get_checks())
    test = configure_authentication_backends(
        ["a", "axes.backends.AxesStandaloneBackend", "b"]
    )
    assert test == ["a", "axes.backends.AxesStandaloneBackend", "b"]
    assert len(registry.get_checks()) == num + 1


def test_configure_middleware():
    """Test that the configure_middleware utility adds the correct middleware to
    the list"""
    num = len(registry.get_checks())
    test = configure_middleware([])
    assert test == [
        "axes.middleware.AxesMiddleware",
        "django.middleware.locale.LocaleMiddleware",
    ]
    assert len(registry.get_checks()) == num

    num = len(registry.get_checks())
    test = configure_middleware(["a", "b"])
    assert test == [
        "axes.middleware.AxesMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "a",
        "b",
    ]
    assert len(registry.get_checks()) == num

    num = len(registry.get_checks())
    test = configure_middleware(
        [
            "a",
            "axes.middleware.AxesMiddleware",
            "django.middleware.locale.LocaleMiddleware",
            "b",
        ]
    )
    assert test == [
        "a",
        "axes.middleware.AxesMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "b",
    ]
    assert len(registry.get_checks()) == num + 2
