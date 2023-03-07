"""
Plugin and Fixtures for pyTest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a ``settings`` and ``patch_settings`` fixtures.

"""
import pytest


@pytest.fixture
def settings():
    """
    Fixture that provides access to current pyApp settings.

    This fixture will raise an error is settings have not been configured.
    """
    import pyapp.conf  # pylint: disable=import-outside-toplevel

    return pyapp.conf.settings


@pytest.fixture
def patch_settings(settings):  # pylint: disable=redefined-outer-name
    """
    Fixture that provides a :class:`pyapp.conf.ModifySettingsContext` instance
    that allows a test to modify settings that will be rolled back after the
    test has completed.
    """
    with settings.modify() as patch:
        yield patch
