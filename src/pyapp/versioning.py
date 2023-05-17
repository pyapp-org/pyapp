"""
Versioning
~~~~~~~~~~

This module provides a method for obtaining the installed version of a named
package. This is used by `pyApp` itself to determine it's version at runtime
to avoid the back-flips required to bake the current version into the package
at build time.

This module is only for compatibility reasons and will be removed in a future.

Recommended replacement is to use ``importlib.metadata.distribution`` directly.

"""

try:
    import importlib_metadata as metadata
except ImportError:
    from importlib import metadata


def get_installed_version(
    package_name: str,
    package_root: str,  # pylint: disable=unused-argument
) -> str:
    """
    Get the version of the currently installed version of a package.

    Provide the name of the package as well as the file location of the root
    package e.g. in your packages `__init__.py` file::

        __version__ = get_installed_version("MyPackage", __file__)

    """
    try:
        dist = metadata.distribution(package_name)
    except metadata.PackageNotFoundError:
        return f"Please install {package_name} via a package."
    else:
        return dist.version
