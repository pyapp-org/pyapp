from unittest import mock
from unittest.mock import patch

from pyapp import versioning


@patch("pyapp.versioning.metadata.distribution")
def test_get_installed_version__found(distribution, monkeypatch):
    """
    Package found with the correct location
    """
    distribution.return_value = mock.Mock(
        spec=versioning.metadata.Distribution, version="1.2.3"
    )

    actual = versioning.get_installed_version(
        "my_package", "/path/to/my_package/__init__.py"
    )

    assert actual == "1.2.3"
    distribution.assert_called_once_with("my_package")


@patch("pyapp.versioning.metadata.distribution")
def test_get_installed_version__not_found(distribution, monkeypatch):
    """
    Package not found
    """
    distribution.side_effect = versioning.metadata.PackageNotFoundError()

    actual = versioning.get_installed_version(
        "my_package", "/path/to/my_package/__init__.py"
    )

    assert actual == "Please install my_package via a package."
    distribution.assert_called_once_with("my_package")
