# This module is a wrapper around the django-rules package
from unittest.mock import patch

import rules
from rules import add_rule, predicate


class NonExistentRuleException(Exception):
    pass


# this is the "private" version, for mocking purposes
def _test_rule(name, user=None, obj=None):
    if not rules.rule_exists(name):
        raise NonExistentRuleException(f"rule {name} does not exist")

    return rules.test_rule(name, user, obj)


def test_rule(*args, **kwargs):
    return _test_rule(*args, **kwargs)


def auto_rule(fn):
    """
    use as decorator, e.g.

    @auto_rule
    def rule_name(user, obj):
        ...


    is shorthand for

    add_rule("rule_name", rule_name_func)

    """
    pred = predicate(fn)
    add_rule(fn.__name__, pred)
    return pred


class patch_rules:
    """
    usage: with mock_rules(can_access_foo=False):
      assert test_client.get(some_view_that_uses_patched_rules).status_code == 403
    """

    def rule_mocker(self, **rule_stubs):
        def exec_rule(rule_name, user=None, obj=None):
            if rule_name in rule_stubs:
                return rule_stubs[rule_name]

            return self.actual_rule_func(rule_name, user, obj)

        return exec_rule

    def __init__(self, **rule_stubs):
        self.actual_rule_func = _test_rule
        self._patch = patch(
            "phac_aspc.rules._test_rule", self.rule_mocker(**rule_stubs)
        )

    def __enter__(self):
        return self._patch.__enter__()

    def __exit__(self, *excp):
        return self._patch.__exit__(*excp)
