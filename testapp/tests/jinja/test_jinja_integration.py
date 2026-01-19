from jinja2 import Environment, pass_context

from phac_aspc.jinja.registry import JinjaRegistry


def test_registry_directly():
    """Test that the JinjaRegistry can be instantiated and used directly."""
    registry = JinjaRegistry()

    # Test adding a global function
    @registry.add_global
    def test_func():
        return "test"

    registry.add_global("another_name", test_func)

    assert registry.globals["test_func"] is test_func
    assert registry.globals["another_name"] is test_func

    @registry.add_global
    class MyClass:
        pass

    registry.add_global("MyClass", MyClass)
    registry.add_global("my_class_alias", MyClass)

    # try w/ context decorator
    @registry.add_global
    @pass_context
    def context_func(context):
        return context.get("test_key", "default_value")

    assert registry.globals["context_func"] is context_func

    # Test getting the environment
    env = registry.get_environment()
    assert isinstance(env, Environment)

    assert env.globals["test_func"]() == "test"


def test_view(client):
    """Test that the view renders the template with the correct context."""
    response = client.get("/with_language_tag/")
    assert response.status_code == 200

    assert "en-ca" in response.content.decode("utf-8")
    assert "fr-ca" in response.content.decode("utf-8")
