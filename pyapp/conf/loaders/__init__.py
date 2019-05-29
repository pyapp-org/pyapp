"""
Loaders are used to load settings from an external source, eg a Python module
(using :py:class:`ModuleLoader`).

A loader provides key/value pairs to the settings container to merge into the
application settings.
"""
import importlib

from typing import Iterator, Tuple, Any, Dict, Type, Union
from yarl import URL

from pyapp.exceptions import InvalidConfiguration
from .base import Loader
from .file_loader import FileLoader
from .http_loader import HttpLoader


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
    def from_url(cls, url: URL) -> Loader:
        """
        Create an instance of :class:`ModuleLoader` from :class:`urllib.parse.ParseResult`.
        """
        return cls(url.path)

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


LoaderType = Type[Loader]


class SettingsLoaderRegistry(Dict[str, LoaderType]):
    """
    Registry of settings loaders
    """

    def register(self, loader: LoaderType) -> LoaderType:
        """
        Register a new loader, this method can be used as decorator

        :param loader: Loader to register

        """
        loader_schemes = getattr(loader, "scheme")
        if isinstance(loader_schemes, str):
            loader_schemes = (loader_schemes,)

        for loader_scheme in loader_schemes:
            self[loader_scheme] = loader

        return loader

    def factory(self, settings_url: Union[str, URL]) -> Loader:
        """
        Factory method that returns a factory suitable for opening the settings uri reference.

        The URI scheme (identifier prior to the first `:`) is used to determine the correct loader.

        :param settings_url: URI that references a settings source.
        :return: Loader instance
        :raises: ValueError

        """
        url = URL(settings_url)
        if not url.scheme:
            # If no scheme is defined assume python module
            return ModuleLoader.from_url(url)

        try:
            return self[url.scheme].from_url(url)
        except KeyError:
            raise InvalidConfiguration(
                f"Unknown scheme `{url.scheme}` in settings URI: {url}"
            )


# Singleton instance
registry = SettingsLoaderRegistry(
    {
        "python": ModuleLoader,
        "file": FileLoader,
        "http": HttpLoader,
        "https": HttpLoader,
    }
)
register = registry.register
factory = registry.factory
