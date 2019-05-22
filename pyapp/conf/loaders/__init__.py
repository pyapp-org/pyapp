"""
Loaders are used to load settings from an external source, eg a Python module
(using :py:class:`ModuleLoader`).

A loader provides key/value pairs to the settings container to merge into the
application settings.
"""
import importlib

from urllib.parse import urlparse, ParseResult

from pyapp.exceptions import InvalidConfiguration
from .file_loader import FileLoader


class ModuleLoader:
    """
    Load configuration from an importable module.

    Loader will load all upper case attributes from the imported module.

    Usage:

        >>> loader = ModuleLoader("name.of.module")
        >>> settings = dict(loader)

    """

    scheme = "python"

    @classmethod
    def from_url(cls, parse_result: ParseResult) -> "ModuleLoader":
        """
        Create an instance of :class:`ModuleLoader` from :class:`urllib.parse.ParseResult`.
        """
        return cls(parse_result.path)

    def __init__(self, module: str):
        """
        :param module: Fully qualify python module path.

        """
        assert module

        self.module = module

    def __iter__(self):
        try:
            mod = importlib.import_module(self.module)
        except ImportError as ex:
            raise InvalidConfiguration(f"Unable to load module: {self}\n{ex}")

        return ((k, getattr(mod, k)) for k in dir(mod) if k.isupper())

    def __str__(self):
        return f"{self.scheme}:{self.module}"


class SettingsLoaderRegistry:
    def __init__(self):
        self.loaders = {
            FileLoader.scheme: FileLoader,
            ModuleLoader.scheme: ModuleLoader,
        }

    def register(self, loader=None, scheme=None):
        """
        Register a new loader, this method can be used as decorator

        :param loader: Loader to register
        :param scheme: Scheme to register this loader for, if supplied scheme must be a attribute of the loader

        """

        def inner(obj):
            loader_scheme = scheme or getattr(obj, "scheme", None)
            assert loader_scheme, "Scheme has not been defined."
            assert hasattr(
                obj, "from_url"
            ), "Settings loaders must implement a from_url method"
            self.loaders[loader_scheme] = obj
            return obj

        return inner(loader) if loader else inner

    def factory(self, settings_url: str) -> ModuleLoader:
        """
        Factory method that returns a factory suitable for opening the settings uri reference.

        The URI scheme (identifier prior to the first `:`) is used to determine the correct loader.

        :param settings_url: URI that references a settings source.
        :return: Loader instance
        :raises: ValueError

        """
        result = urlparse(settings_url)
        if not result.scheme:
            # If no scheme is defined assume python module
            return ModuleLoader.from_url(result)

        try:
            return self.loaders[result.scheme].from_url(result)
        except KeyError:
            raise InvalidConfiguration(
                f"Unknown scheme `{result.scheme}` in settings URI: {result}"
            )


# Singleton instance
registry = SettingsLoaderRegistry()
register = registry.register
factory = registry.factory
