from phac_aspc.rules import (
    # must be imported in form that doesn't start with test_
    # otherwise pytest will try to run it as a test
    test_rule as func_test_rule,
    patch_rules,
    add_rule,
    auto_rule,
)


def test_rules():
    @auto_rule
    def has_foo_access(user, obj):
        return True

    # also test manually added rule
    def has_bar_access_func(user, obj):
        return False

    add_rule("has_bar_access", has_bar_access_func)

    # test_rule works with 1, 2, or 3 arguments
    assert func_test_rule("has_foo_access")
    assert func_test_rule("has_foo_access", 1)
    assert func_test_rule("has_foo_access", 1, 1)
    assert not func_test_rule("has_bar_access")

    with patch_rules(has_foo_access=False, has_bar_access=True):
        assert func_test_rule("has_bar_access")
        assert not func_test_rule("has_foo_access")

    # rules are returned to normal after patch_rules
    assert not func_test_rule("has_bar_access")
    assert func_test_rule("has_foo_access")
