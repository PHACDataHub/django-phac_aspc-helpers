import inspect

from jinja2 import Environment, FileSystemLoader


class JinjaRegistry:
    def __init__(self):
        self.globals = {}
        self.filters = {}
        self.tests = {}
        self.extensions = []

    def include_default_helpers(self):
        from phac_aspc.jinja import standard_helpers

    def get_environment(self, **options):

        self.include_default_helpers()

        env = Environment(**options)
        env.globals.update(self.globals)
        env.filters.update(self.filters)
        env.tests.update(self.tests)
        for extension in self.extensions:
            env.add_extension(extension)

        return env

    def add_extension(self, extension):
        """
        Add a Jinja2 extension to the environment.
        """
        self.extensions.append(extension)

    @staticmethod
    def _get_name_and_value(name=None, value=None):
        if value is None:
            if inspect.isfunction(name) or inspect.isclass(name):
                value = name
                name = value.__name__
                return name, value
            else:
                raise ValueError(
                    "name must be provided for non-function/class objects"
                )

        return name, value

    def add_global(self, name=None, value=None):
        name, value = self._get_name_and_value(name, value)

        self.globals[name] = value

        return value

    def add_filter(self, name=None, value=None):
        name, value = self._get_name_and_value(name, value)

        self.filters[name] = value

        return value

    def add_test(self, name=None, value=None):
        name, value = self._get_name_and_value(name, value)

        self.tests[name] = value

        return value


registry = JinjaRegistry()
