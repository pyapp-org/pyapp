"""
Conf Loaders
~~~~~~~~~~~~

Loaders are used to load settings from an external source, eg a Python module
(using :py:class:`ModuleLoader`).

A loader provides key/value pairs to the settings container to merge into the
application settings.
"""
import importlib
from typing import Any
from typing import Dict
from typing import Iterator
from typing import Tuple
from typing import Type
from typing import Union

from yarl import URL

from pyapp.conf.loaders.base import Loader
from pyapp.conf.loaders.file_loader import FileLoader
from pyapp.conf.loaders.http_loader import HttpLoader
from pyapp.exceptions import InvalidConfiguration


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
        return f"{self.scheme}:{self.module}"  # pylint: disable=no-member


class ObjectLoader(Loader):
    """
    Load configuration variables from any object. This can be used to mirror
    settings from Django settings.

    Loader will only read UPPERCASE attributes from the object.

    Usage:

        >>> from django.conf import settings as django_settings
        >>> from pyapp.conf import settings as pyapp_settings
        >>> loader = ObjectLoader(django_settings)
        >>> pyapp_settings.load(loader)

    .. versionadded:: 4.2

    """

    @classmethod
    def from_url(cls, url: URL) -> "Loader":
        raise NotImplementedError("This loader does not support from_url.")

    def __init__(self, obj: object):
        self.obj = obj

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        obj = self.obj
        return ((k, getattr(obj, k)) for k in dir(obj) if k.isupper())


LoaderType = Type[Loader]


# TODO: Remove when pylint handles typing.Dict correctly  pylint: disable=fixme
# pylint: disable=no-member,unsubscriptable-object,unsupported-assignment-operation
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
registry = SettingsLoaderRegistry(  # pylint: disable=invalid-name
    {
        "python": ModuleLoader,
        "file": FileLoader,
        "http": HttpLoader,
        "https": HttpLoader,
    }
)
register = registry.register  # pylint: disable=invalid-name
factory = registry.factory  # pylint: disable=invalid-name
