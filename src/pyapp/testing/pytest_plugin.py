"""
Plugin and Fixtures for pyTest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides ``settings``, ``patch_settings``, ``patch_feature_flags`` and ``check_registry`` fixtures.

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


@pytest.fixture
def patch_feature_flags():  # pylint: disable=redefined-outer-name
    """
    Fixture that provides a :class:`pyapp.feature_flags.ModifyFeatureFlagsContext`
    instance that allows a test to modify feature flags that will be rolled back
    after the test has completed.
    """
    from pyapp import feature_flags

    with feature_flags.DEFAULT.modify() as patch:
        yield patch


@pytest.fixture
def check_registry(monkeypatch):  # pylint: disable=redefined-outer-name
    """
    Fixture that provides access to a check registry.

    Returned registry will be empty and will replace the default registry from
    ``pyapp.checks.registry`` and ``pyapp.checks.register`` during the test.
    """
    import pyapp.checks  # pylint: disable=import-outside-toplevel

    registry = pyapp.checks.registry.CheckRegistry()
    monkeypatch.setattr("pyapp.checks.registry", registry)
    monkeypatch.setattr("pyapp.checks.register", registry.register)

    return registry
