"""Unit tests for utils.py"""
from copy import deepcopy
import os
import subprocess
from unittest.mock import patch

from django.core.checks.registry import registry
import pytest

from phac_aspc.django.settings.utils import (
    trigger_configuration_warning,
    warn_and_remove,
    configure_apps,
    configure_authentication_backends,
    configure_middleware,
    is_running_tests,
    find_env_file,
    get_env,
    get_env_value,
    global_from_env,
)


@pytest.fixture()
def freeze_environ():
    """The environ package hoists values from .env files in to env vars, can be
    a source of cross-test contamination. This fixture rolls back any changes made
    made to os.environ during a test.

    Note: as per https://docs.python.org/3/library/os.html?highlight=environ#os.environ,
    modifying the os.environ mapping directly is actually the correct way to manage env vars
    """
    pre_test_environ = deepcopy(os.environ)
    yield
    for key, value in os.environ.items():
        if not key in pre_test_environ:
            del os.environ[key]
        else:
            os.environ[key] = value


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
    assert test == [
        "modeltranslation",
        "axes",
        "phac_aspc.django.helpers",
        "rules.apps.AutodiscoverRulesConfig",
    ]
    assert len(registry.get_checks()) == num

    num = len(registry.get_checks())
    test = configure_apps(["a", "b"])
    assert test == [
        "modeltranslation",
        "axes",
        "a",
        "b",
        "phac_aspc.django.helpers",
        "rules.apps.AutodiscoverRulesConfig",
    ]
    assert len(registry.get_checks()) == num

    num = len(registry.get_checks())
    test = configure_apps(["a", "axes", "b"])
    assert test == [
        "modeltranslation",
        "a",
        "axes",
        "b",
        "phac_aspc.django.helpers",
        "rules.apps.AutodiscoverRulesConfig",
    ]
    assert len(registry.get_checks()) == num + 1

    num = len(registry.get_checks())
    test = configure_apps(["phac_aspc.django.helpers", "axes", "b"])
    assert test == [
        "modeltranslation",
        "phac_aspc.django.helpers",
        "axes",
        "b",
        "rules.apps.AutodiscoverRulesConfig",
    ]
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
        "django_structlog.middlewares.RequestMiddleware",
    ]
    assert len(registry.get_checks()) == num

    num = len(registry.get_checks())
    test = configure_middleware(["a", "b"])
    assert test == [
        "axes.middleware.AxesMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django_structlog.middlewares.RequestMiddleware",
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
            "django_structlog.middlewares.RequestMiddleware",
            "b",
        ]
    )
    assert test == [
        "a",
        "axes.middleware.AxesMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django_structlog.middlewares.RequestMiddleware",
        "b",
    ]
    assert len(registry.get_checks()) == num + 3


def test_is_running_tests_returns_true_inside_test_execution_environment():
    assert is_running_tests()


def test_is_running_tests_returns_false_outside_test_execution_environment():
    # hacky, but because this test needs to assert that is_running_tests() is false
    # OUTSIDE of the test environment, we need to run a non-test sub-process and read
    # back the `is_running_tests()` value from there

    manage_py_path = os.path.join(
        os.getcwd(),
        "manage.py",
    )
    assert os.path.isfile(manage_py_path)

    non_test_execution_process = subprocess.run(
        [
            manage_py_path,
            "shell",
            "--command",
            # pylint: disable=line-too-long
            f"from {is_running_tests.__module__} import is_running_tests; print(is_running_tests())",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert non_test_execution_process.stdout.strip() == "False"


def test_find_env_file_returns_none_when_no_dot_env_found(tmp_path):
    # WARNING: this test might fail, on the slim chance that some other
    # .env file is found between the temp file location and the system root...
    # but that should be highly unlikely
    assert find_env_file(tmp_path) is None


def test_find_env_file_returns_ancestor_env_path(tmp_path):
    env_path = os.path.join(tmp_path, ".env")

    env_file = open(env_path, "w", encoding="UTF-8")
    env_file.write("")
    env_file.close()

    sub_dir = os.path.join(tmp_path, "sub_dir")
    os.mkdir(sub_dir)

    sub_sub_dir = os.path.join(sub_dir, "sub_sub_dir")
    os.mkdir(sub_sub_dir)

    assert find_env_file(sub_sub_dir) == env_path


def test_get_env(tmp_path, freeze_environ):
    prefix = "ENV_VAR_"

    env_var = f"{prefix}FROM_FILE"

    env_path = os.path.join(tmp_path, ".env")

    env_file = open(env_path, "w", encoding="UTF-8")
    env_file.write(f"{env_var}=true")
    env_file.close()

    with patch(
        f"{find_env_file.__module__}.{find_env_file.__name__}",
        return_value=env_path,
    ):
        env = get_env(
            prefix=prefix,
            FROM_FILE=(bool, False),
        )

        assert env(env_var) is True


def test_get_env_value(tmp_path, settings, freeze_environ):
    prefix = "ENV_VAR_"

    default = "default"
    not_default = "not default"

    env_path = os.path.join(tmp_path, ".env")

    env_file = open(env_path, "w", encoding="UTF-8")
    env_file.write(f"{prefix}FROM_FILE={not_default}")
    env_file.close()

    setattr(settings, f"{prefix}FROM_SETTINGS", not_default)

    with patch(
        f"{find_env_file.__module__}.{find_env_file.__name__}",
        return_value=env_path,
    ):
        env = get_env(
            prefix=prefix,
            FROM_FILE=(str, default),
            FROM_SETTINGS=(str, default),
            FROM_DEFAULT=(str, default),
        )

        assert get_env_value(env, "FROM_FILE", prefix=prefix) == not_default
        assert get_env_value(env, "FROM_SETTINGS", prefix=prefix) == not_default
        assert get_env_value(env, "FROM_DEFAULT", prefix=prefix) == default


def test_global_from_env(tmp_path, settings, freeze_environ):
    default = "default"
    not_default = "not default"

    setattr(settings, "GLOBAL_FROM_SETTINGS", not_default)

    global_from_env(
        prefix="",
        GLOBAL_FROM_SETTINGS=(str, default),
        GLOBAL_FROM_DEFAULT=(str, default),
    )

    assert GLOBAL_FROM_SETTINGS == not_default  # pylint: disable=undefined-variable
    assert GLOBAL_FROM_DEFAULT == default  # pylint: disable=undefined-variable
