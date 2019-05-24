"""
Loaders are used to load settings from an external source, eg a Python module
(using :py:class:`ModuleLoader`).

A loader provides key/value pairs to the settings container to merge into the
application settings.
"""
import importlib

from typing import Iterator, Tuple, Any, Dict, Type
from urllib.parse import urlparse, ParseResult

from pyapp.exceptions import InvalidConfiguration
from .base import Loader
from .file_loader import FileLoader


class ModuleLoader(Loader):
    """
    Load configuration from an importable module.

    Loader will load all upper case attributes from the imported module.

    Usage:

        >>> loader = ModuleLoader("name.of.module")
        >>> settings = dict(loader)

    """

    scheme = "python"

    @classmethod
    def from_url(cls, parse_result: ParseResult) -> Loader:
        """
        Create an instance of :class:`ModuleLoader` from :class:`urllib.parse.ParseResult`.
        """
        return cls(parse_result.path)

    def __init__(self, module: str):
        """
        :param module: Fully qualify python module path.

        """
        self.module = module

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        try:
            mod = importlib.import_module(self.module)
        except ImportError as ex:
            raise InvalidConfiguration(f"Unable to load module: {self}\n{ex}")

        return ((k, getattr(mod, k)) for k in dir(mod) if k.isupper())

    def __str__(self):
        return f"{self.scheme}:{self.module}"


class SettingsLoaderRegistry:
    """
    Registry of settings loaders
    """
    def __init__(self):
        self.loaders: Dict[str, Type[Loader]] = {}

        # Register builtin loaders
        self.register(ModuleLoader)
        self.register(FileLoader)

    def register(self, loader: Type[Loader] = None, scheme: str = None):
        """
        Register a new loader, this method can be used as decorator

        :param loader: Loader to register
        :param scheme: Scheme to register this loader for, if supplied scheme must be a attribute of the loader

        """

        def inner(obj):
            loader_schemes = scheme or getattr(obj, "scheme", None)
            if isinstance(loader_schemes, str):
                loader_schemes = (loader_schemes,)

            for loader_scheme in loader_schemes:
                self.loaders[loader_scheme] = obj

            return obj

        return inner(loader) if loader else inner

    def factory(self, settings_url: str) -> Loader:
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
