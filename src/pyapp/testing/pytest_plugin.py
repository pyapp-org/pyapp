"""
Plugin and Fixtures for pyTest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides ``settings``, ``patch_settings``, ``patch_feature_flags``,
``patch_injection`` and ``check_registry`` fixtures.

"""

import pytest

import pyapp.checks
import pyapp.conf
import pyapp.feature_flags
import pyapp.injection


@pytest.fixture
def settings() -> pyapp.conf.Settings:
    """
    Fixture that provides access to current pyApp settings.

    This fixture will raise an error is settings have not been configured.
    """
    return pyapp.conf.settings


@pytest.fixture
def patch_settings(settings) -> pyapp.conf.ModifySettingsContext:
    """
    Fixture that provides a :class:`pyapp.conf.ModifySettingsContext` instance
    that allows a test to modify settings that will be rolled back after the
    test has completed.
    """
    with settings.modify() as patch:
        yield patch


@pytest.fixture
def pyapp_feature_flags() -> pyapp.feature_flags.FeatureFlags:
    """
    Fixture that provides a :class:`pyapp.feature_flags.ModifyFeatureFlagsContext`
    instance that allows a test to modify feature flags that will be rolled back
    after the test has completed.
    """
    return pyapp.feature_flags.DEFAULT


@pytest.fixture
def patch_feature_flags(
    pyapp_feature_flags,
) -> pyapp.feature_flags.ModifyFeatureFlagsContext:
    """
    Fixture that provides a :class:`pyapp.feature_flags.ModifyFeatureFlagsContext`
    instance that allows a test to modify feature flags that will be rolled back
    after the test has completed.
    """
    with pyapp_feature_flags.modify() as patch:
        yield patch


@pytest.fixture
def pyapp_factory_registry() -> pyapp.injection.FactoryRegistry:
    """
    Fixture that provides the default factory registry used by the ``@inject``
    decorator.
    """
    return pyapp.injection.default_registry


@pytest.fixture
def patch_injection(
    pyapp_factory_registry,
) -> pyapp.injection.ModifyFactoryRegistryContext:
    """
    Fixture that proces a :class:`pyapp.injection.ModifyFactoryRegistryContext`
    instance that allows a test to modify factories mapped to abstract types
    used by the ``@inject`` decorator. Any changes to the registry are rolled
    back after the test has completed.
    """
    with pyapp_factory_registry.modify() as patch:
        yield patch


@pytest.fixture
def check_registry(monkeypatch) -> pyapp.checks.registry.CheckRegistry:
    """
    Fixture that provides access to a check registry.

    Returned registry will be empty and will replace the default registry from
    ``pyapp.checks.registry`` and ``pyapp.checks.register`` during the test.
    """
    registry = pyapp.checks.registry.CheckRegistry()
    monkeypatch.setattr("pyapp.checks.registry", registry)
    monkeypatch.setattr("pyapp.checks.register", registry.register)
    return registry
