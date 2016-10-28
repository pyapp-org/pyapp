from __future__ import absolute_import

from .file_loader import FileLoader
from .module_loader import ModuleLoader


LOADERS = {
    FileLoader.scheme: FileLoader,
    ModuleLoader.scheme: ModuleLoader,
}


def factory(settings_uri):
    """
    Factory method that returns a factory suitable for opening the settings uri reference.

    The URI scheme (identifier prior to the first `:`) is used to determine the correct loader.

    :param settings_uri: URI that references a settings source.
    :type settings_uri: str
    :return: Loader instance
    :raises: ValueError

    """
    scheme, _ = settings_uri.split(':', 1)

    try:
        return LOADERS[scheme](settings_uri)
    except KeyError:
        raise ValueError("Unknown scheme `{}` in settings URI: {}".format(scheme, settings_uri))
