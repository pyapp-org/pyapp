import pytest

import pyapp.conf


class TestSettings(object):
    def test_configure(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings')

        assert 'python:tests.settings' in settings.SETTINGS_SOURCES
        assert hasattr(settings, 'UPPER_VALUE')
        assert not hasattr(settings, 'lower_value')
        assert not hasattr(settings, 'mixed_VALUE')

    def test_configure__from_runtime_parameter(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings', 'tests.runtime_settings')

        assert 'python:tests.runtime_settings' in settings.SETTINGS_SOURCES
        assert hasattr(settings, 'UPPER_VALUE')
        assert hasattr(settings, 'RUNTIME_VALUE')
        assert not hasattr(settings, 'lower_value')
        assert not hasattr(settings, 'mixed_VALUE')

    def test_configure__from_environment(self, monkeypatch):
        monkeypatch.setenv('PYAPP_SETTINGS', 'tests.runtime_settings')

        settings = pyapp.conf.Settings()
        settings.configure('tests.settings')

        assert 'python:tests.runtime_settings' in settings.SETTINGS_SOURCES
        assert hasattr(settings, 'UPPER_VALUE')
        assert hasattr(settings, 'RUNTIME_VALUE')
        assert not hasattr(settings, 'lower_value')
        assert not hasattr(settings, 'mixed_VALUE')

    def test_load__duplicate_settings_file(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings', 'tests.runtime_settings')

        with pytest.warns(ImportWarning):
            settings.load(pyapp.conf.ModuleLoader('tests.runtime_settings'))

    def test_repr__un_configured(self):
        settings = pyapp.conf.Settings()

        assert repr(settings) == 'Settings(UN-CONFIGURED)'

    def test_repr__configured(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings')

        assert repr(settings) == "Settings(['python:tests.settings'])"
