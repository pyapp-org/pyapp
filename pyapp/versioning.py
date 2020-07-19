"""
Versioning
~~~~~~~~~~

This module provides a method for obtaining the installed version of a named
package. This is used by `pyApp` itself to determine it's version at runtime
to avoid the back-flips required to bake the current version into the package
at build time.

"""
from pathlib import Path

from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution


def get_installed_version(package_name: str, package_root: str):
    """
    Get the version of the currently installed version of a package.

    Provide the name of the package as well as the file location of the root
    package eg in your packages `__init__.py` file::

        __version__ = get_installed_version("MyPackage", __file__)


    .. info:: The file path is used to confirm the package info provided by
        `pkg_resources` is the expected package.

    """
    here = Path(package_root)

    try:
        dist = get_distribution(package_name)
        if not here.as_posix().startswith(dist.location):
            # not installed, but there is another version that *is*
            raise DistributionNotFound
    except DistributionNotFound:
        return f"Please install {package_name} via a package."
    else:
        return dist.version
