import pytest

import pyapp.conf


class TestSettings:
    @pytest.fixture
    def target(self) -> pyapp.conf.Settings:
        target = pyapp.conf.Settings()
        target.configure(["tests.settings"])
        return target

    def test_configure(self, target: pyapp.conf.Settings):
        assert "python:tests.settings" in target.SETTINGS_SOURCES
        assert hasattr(target, "UPPER_VALUE")
        assert not hasattr(target, "lower_value")
        assert not hasattr(target, "mixed_VALUE")

    def test_configure__from_runtime_parameter(self):
        target = pyapp.conf.Settings()
        target.configure(["tests.settings"], "tests.runtime_settings")

        assert "python:tests.runtime_settings" in target.SETTINGS_SOURCES
        assert hasattr(target, "UPPER_VALUE")
        assert hasattr(target, "RUNTIME_VALUE")
        assert not hasattr(target, "lower_value")
        assert not hasattr(target, "mixed_VALUE")

    def test_configure__from_environment(self, monkeypatch):
        monkeypatch.setenv("PYAPP_SETTINGS", "tests.runtime_settings")

        target = pyapp.conf.Settings()
        target.configure(["tests.settings"])

        assert "python:tests.runtime_settings" in target.SETTINGS_SOURCES
        assert hasattr(target, "UPPER_VALUE")
        assert hasattr(target, "RUNTIME_VALUE")
        assert not hasattr(target, "lower_value")
        assert not hasattr(target, "mixed_VALUE")

    def test_configure__additional_loaders(self):
        target = pyapp.conf.Settings()

        with pytest.warns(ImportWarning):
            target.configure(
                ["tests.settings"],
                "tests.runtime_settings",
                [pyapp.conf.ModuleLoader("tests.runtime_settings_with_imports")],
            )

        assert "python:tests.runtime_settings_with_imports" in target.SETTINGS_SOURCES
        assert "python:tests.runtime_settings" in target.SETTINGS_SOURCES

    def test_load__duplicate_settings_file(self):
        target = pyapp.conf.Settings()
        target.configure(["tests.settings"], "tests.runtime_settings")

        with pytest.warns(ImportWarning):
            target.load(pyapp.conf.ModuleLoader("tests.runtime_settings"))

    def test_load__specify_include_settings(self):
        target = pyapp.conf.Settings()
        target.configure(["tests.settings"], "tests.runtime_settings_with_imports")

        assert "python:tests.runtime_settings_with_imports" in target.SETTINGS_SOURCES
        assert "python:tests.runtime_settings" in target.SETTINGS_SOURCES
        assert not hasattr(target, "INCLUDE_SETTINGS")
        assert hasattr(target, "TEST_VALUE")
        assert hasattr(target, "RUNTIME_VALUE")

    def test_repr__un_configured(self):
        target = pyapp.conf.Settings()

        assert not target.is_configured
        assert repr(target) == "Settings(UN-CONFIGURED)"

    def test_repr__configured(self, target: pyapp.conf.Settings):
        assert target.is_configured
        assert repr(target) == "Settings(['python:tests.settings'])"

    def test_modify__change_a_setting(self, target: pyapp.conf.Settings):
        with target.modify() as patch:
            patch.SETTING_1 = 10
            patch.SETTING_2 = 20

            assert target.SETTING_1 == 10
            assert patch.SETTING_1 == 10
            assert target.SETTING_2 == 20
            assert patch.SETTING_2 == 20

        assert target.SETTING_1 == 1
        assert target.SETTING_2 == 2

    def test_modify__add_a_setting(self, target: pyapp.conf.Settings):
        with target.modify() as patch:
            patch.SETTING_6 = 60

            assert target.SETTING_6 == 60
            assert patch.SETTING_6 == 60

        assert not hasattr(target, "SETTING_6")

    def test_modify__remove_a_setting(self, target: pyapp.conf.Settings):
        with target.modify() as patch:
            del patch.SETTING_3
            del patch.SETTING_6

            assert not hasattr(target, "SETTING_3")
            assert not hasattr(target, "SETTING_6")

        assert target.SETTING_3 == 3
        assert not hasattr(target, "SETTING_6")

    def test_modify__multiple_changes_reversed(self, target: pyapp.conf.Settings):
        with target.modify() as patch:
            patch.SETTING_1 = 10
            del patch.SETTING_1
            patch.SETTING_2 = 20
            patch.SETTING_1 = 30
            del patch.SETTING_3
            patch.SETTING_6 = 60

            assert target.SETTING_1 == 30
            assert target.SETTING_2 == 20
            assert not hasattr(target, "SETTING_3")
            assert target.SETTING_6 == 60

        assert target.SETTING_1 == 1
        assert target.SETTING_2 == 2
        assert target.SETTING_3 == 3
        assert not hasattr(target, "SETTING_6")
