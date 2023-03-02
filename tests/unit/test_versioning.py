from unittest import mock

from pkg_resources import Distribution

from pyapp import versioning


def test_get_installed_version__found(monkeypatch):
    """
    Package found with the correct location
    """
    mock_get_distribution = mock.Mock(
        return_value=Distribution(location="/path/to/my_package", version="1.2.3")
    )
    monkeypatch.setattr(versioning, "get_distribution", mock_get_distribution)

    actual = versioning.get_installed_version(
        "my_package", "/path/to/my_package/__init__.py"
    )

    assert actual == "1.2.3"
    mock_get_distribution.assert_called_once_with("my_package")


def test_get_installed_version__not_found(monkeypatch):
    """
    Package not found
    """
    mock_get_distribution = mock.Mock(side_effect=versioning.DistributionNotFound())
    monkeypatch.setattr(versioning, "get_distribution", mock_get_distribution)

    actual = versioning.get_installed_version(
        "my_package", "/path/to/my_package/__init__.py"
    )

    assert actual == "Please install my_package via a package."
    mock_get_distribution.assert_called_once_with("my_package")


def test_get_installed_version__found_but_wrong_location(monkeypatch):
    """
    Package not found
    """
    mock_get_distribution = mock.Mock(
        return_value=Distribution(location="/path/to/my_package", version="1.2.3")
    )
    monkeypatch.setattr(versioning, "get_distribution", mock_get_distribution)

    actual = versioning.get_installed_version(
        "my_package", "/wrong/path/to/my_package/__init__.py"
    )

    assert actual == "Please install my_package via a package."
    mock_get_distribution.assert_called_once_with("my_package")
