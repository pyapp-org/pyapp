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

    def test_configure__additional_loaders(self):
        settings = pyapp.conf.Settings()

        with pytest.warns(ImportWarning):
            settings.configure('tests.settings', 'tests.runtime_settings', [
                pyapp.conf.ModuleLoader('tests.runtime_settings_with_imports')
            ])

        assert 'python:tests.runtime_settings_with_imports' in settings.SETTINGS_SOURCES
        assert 'python:tests.runtime_settings' in settings.SETTINGS_SOURCES

    def test_load__duplicate_settings_file(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings', 'tests.runtime_settings')

        with pytest.warns(ImportWarning):
            settings.load(pyapp.conf.ModuleLoader('tests.runtime_settings'))

    def test_load__specify_include_settings(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings', 'tests.runtime_settings_with_imports')

        assert 'python:tests.runtime_settings_with_imports' in settings.SETTINGS_SOURCES
        assert 'python:tests.runtime_settings' in settings.SETTINGS_SOURCES
        assert not hasattr(settings, 'INCLUDE_SETTINGS')
        assert hasattr(settings, 'TEST_VALUE')
        assert hasattr(settings, 'RUNTIME_VALUE')

    def test_repr__un_configured(self):
        settings = pyapp.conf.Settings()

        assert not settings.is_configured
        assert repr(settings) == 'Settings(UN-CONFIGURED)'

    def test_repr__configured(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings')

        assert settings.is_configured
        assert repr(settings) == "Settings(['python:tests.settings'])"

    def test_modify__change_a_setting(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings')

        with settings.modify() as patch:
            patch.SETTING_1 = 10
            patch.SETTING_2 = 20

            assert settings.SETTING_1 == 10
            assert patch.SETTING_1 == 10
            assert settings.SETTING_2 == 20
            assert patch.SETTING_2 == 20

        assert settings.SETTING_1 == 1
        assert settings.SETTING_2 == 2

    def test_modify__add_a_setting(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings')

        with settings.modify() as patch:
            patch.SETTING_6 = 60

            assert settings.SETTING_6 == 60
            assert patch.SETTING_6 == 60

        assert not hasattr(settings, 'SETTING_6')

    def test_modify__remove_a_setting(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings')

        with settings.modify() as patch:
            del patch.SETTING_3
            del patch.SETTING_6

            assert not hasattr(settings, 'SETTING_3')
            assert not hasattr(settings, 'SETTING_6')

        assert settings.SETTING_3 == 3
        assert not hasattr(settings, 'SETTING_6')

    def test_modify__multiple_changes_reversed(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings')

        with settings.modify() as patch:
            patch.SETTING_1 = 10
            del patch.SETTING_1
            patch.SETTING_2 = 20
            patch.SETTING_1 = 30
            del patch.SETTING_3
            patch.SETTING_6 = 60

            assert settings.SETTING_1 == 30
            assert settings.SETTING_2 == 20
            assert not hasattr(settings, 'SETTING_3')
            assert settings.SETTING_6 == 60

        assert settings.SETTING_1 == 1
        assert settings.SETTING_2 == 2
        assert settings.SETTING_3 == 3
        assert not hasattr(settings, 'SETTING_6')
