"""
Enables support for executing code when all django apps are ready.
"""
# Define a singleton that will contain the functions to be fired
# on ready.
ready_hooks = []


def execute_when_ready(func):
    """
    Registers a function that will be delayed until all django apps are ready.
    """
    ready_hooks.append(func)


def process_ready_hooks():
    """
    Process the registered hooks.

    This should occur after the models are loaded by Django, for example from
    the AppConfig's ready function.
    """
    for hook in ready_hooks:
        hook()

    ready_hooks.clear()
