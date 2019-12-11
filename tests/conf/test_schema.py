import pytest

from pyapp.conf import schema
from pyapp.conf.loaders import ModuleLoader


class TestSettingsSchema:
    @pytest.fixture
    def target(self):
        loader = ModuleLoader("tests.settings")
        settings_schema = schema.SettingsSchema()
        settings_schema.append_loader(loader)
        return settings_schema

    def test_append_loader(self):
        loader = ModuleLoader("tests.settings")

        target = schema.SettingsSchema()
        actual = target.append_loader(loader)

        assert actual == []

    @pytest.mark.parametrize("key, value", (("SETTING_1", 42), ("UPPER_VALUE", "abc")))
    def test_validate_value__valid_values(self, target, key, value):
        target.validate_value(key, value)

    @pytest.mark.parametrize("key, value", (("SETTING_1", "abc"), ("UPPER_VALUE", 123)))
    def test_validate_value__invalid_values(self, target, key, value):
        with pytest.raises(schema.ValidationError):
            target.validate_value(key, value)
