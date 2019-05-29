from pathlib import Path
from pkg_resources import get_distribution, DistributionNotFound


def get_installed_version(package_name: str, package_root: str):
    """
    Get the version of the currently installed version of a package.
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
