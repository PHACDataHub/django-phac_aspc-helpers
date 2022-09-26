"""
Ready unit tests
"""
from unittest.mock import MagicMock

from phac_aspc.django.helpers.ready import process_ready_hooks, execute_when_ready, ready_hooks


def test_execute_ready():
    """
    Test that functions registered with `execute_when_ready` are added to the
    queue, called by `process_ready_hooks` and removed.
    """
    func = MagicMock()
    execute_when_ready(func)
    assert len(ready_hooks) == 1
    assert ready_hooks[0] == func
    process_ready_hooks()
    assert func.called
    assert len(ready_hooks) == 0
