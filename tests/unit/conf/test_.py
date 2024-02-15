import json
from io import BytesIO, StringIO
from unittest.mock import patch

import pyapp.conf
import pytest


class TestSettings:
    @pytest.fixture
    def target(self) -> pyapp.conf.Settings:
        target = pyapp.conf.Settings()
        target.configure("tests.settings")
        return target

    def test_ensure_readonly(self, target: pyapp.conf.Settings):
        with pytest.raises(AttributeError, match="Readonly object"):
            target.EEK = True

    def test_configure(self, target: pyapp.conf.Settings):
        assert "python:tests.settings" in target.SETTINGS_SOURCES
        assert hasattr(target, "UPPER_VALUE")
        assert not hasattr(target, "lower_value")
        assert not hasattr(target, "mixed_VALUE")

    def test_configure__from_runtime_parameter(self):
        target = pyapp.conf.Settings()
        target.configure("tests.settings", "tests.runtime_settings")

        assert "python:tests.runtime_settings" in target.SETTINGS_SOURCES
        assert hasattr(target, "UPPER_VALUE")
        assert hasattr(target, "RUNTIME_VALUE")
        assert not hasattr(target, "lower_value")
        assert not hasattr(target, "mixed_VALUE")

    def test_configure__with_a_list_of_settings(self):
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
        target.configure("tests.settings")

        assert "python:tests.runtime_settings" in target.SETTINGS_SOURCES
        assert hasattr(target, "UPPER_VALUE")
        assert hasattr(target, "RUNTIME_VALUE")
        assert not hasattr(target, "lower_value")
        assert not hasattr(target, "mixed_VALUE")

    def test_configure__additional_loaders(self):
        target = pyapp.conf.Settings()

        with pytest.warns(ImportWarning):
            target.configure(
                "tests.settings",
                "tests.runtime_settings",
                [pyapp.conf.ModuleLoader("tests.runtime_settings_with_imports")],
            )

        assert "python:tests.runtime_settings_with_imports" in target.SETTINGS_SOURCES
        assert "python:tests.runtime_settings" in target.SETTINGS_SOURCES

    def test_load__duplicate_settings_file(self):
        target = pyapp.conf.Settings()
        target.configure("tests.settings", "tests.runtime_settings")

        with pytest.warns(ImportWarning):
            target.load(pyapp.conf.ModuleLoader("tests.runtime_settings"))

    def test_load__specify_include_settings(self):
        target = pyapp.conf.Settings()
        target.configure("tests.settings", "tests.runtime_settings_with_imports")

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

    def test_modify__reset_settings(self, target: pyapp.conf.Settings):
        known_keys = {
            "UPPER_VALUE",
            "SETTING_2",
            "TEST_NAMED_FACTORY",
            "TEST_ALIAS_FACTORY",
            "TEST_PROVIDERS",
        }

        initial_keys = target.keys

        with target.modify() as patch:
            patch.reset_settings()

            assert all(
                not hasattr(target, key) for key in known_keys
            ), "Custom keys still exist"
            assert [] == target.SETTINGS_SOURCES, "Sources have not been cleared"
            assert not target.is_configured, "Is still listed as configured"
            assert isinstance(target.LOGGING, dict), "Base settings missing"

        # Check items have been restored
        assert initial_keys == target.keys, "All settings not restored"
        assert [
            "python:tests.settings"
        ] == target.SETTINGS_SOURCES, "Sources not restored"

    def test_getitem(self, target: pyapp.conf.Settings):
        actual = target["UPPER_VALUE"]

        assert actual == "foo"


class TestExportRestoreSettings:
    def test_roundtrip_default_serialiser(self, monkeypatch):
        file = BytesIO()

        source_settings = pyapp.conf.Settings()
        source_settings.__dict__["FOO"] = "foo"
        source_settings.__dict__["BAR"] = "bar"
        source_settings.SETTINGS_SOURCES.append("self")
        with patch("pyapp.conf.settings", source_settings):
            pyapp.conf.export_settings(file)

            assert len(file.getvalue()) > 0

        file.seek(0)

        target_settings = pyapp.conf.Settings()
        with patch("pyapp.conf.settings", target_settings):
            pyapp.conf.restore_settings(file)

            assert target_settings.FOO == source_settings.FOO
            assert target_settings.BAR == source_settings.BAR
            assert target_settings.SETTINGS_SOURCES == source_settings.SETTINGS_SOURCES

    def test_roundtrip_json_serialiser(self, monkeypatch):
        file = StringIO()

        source_settings = pyapp.conf.Settings()
        source_settings.__dict__["FOO"] = "foo"
        source_settings.__dict__["BAR"] = "bar"
        source_settings.SETTINGS_SOURCES.append("self")
        with patch("pyapp.conf.settings", source_settings):
            pyapp.conf.export_settings(file, serialiser=json)

            assert len(file.getvalue()) > 0

        file.seek(0)

        target_settings = pyapp.conf.Settings()
        with patch("pyapp.conf.settings", target_settings):
            pyapp.conf.restore_settings(file, serialiser=json)

            assert target_settings.FOO == source_settings.FOO
            assert target_settings.BAR == source_settings.BAR
            assert target_settings.SETTINGS_SOURCES == source_settings.SETTINGS_SOURCES
