# Test only upper values are included
from typing import Sequence

from pyapp.typed_settings import NamedConfig, NamedPluginConfig, SettingsDef


class MySettings(SettingsDef):
    UPPER_VALUE: str = "foo"
    lower_value: str = "bar"
    mixed_VALUE: str = "eek"

    # Helpful test placeholders.
    SETTING_1: int = 1
    SETTING_2: int = 2
    SETTING_3: int = 3
    SETTING_4: int = 4
    SETTING_5: int = 5

    # Factory sample values
    TEST_NAMED_FACTORY: NamedPluginConfig = {
        "default": ("tests.unit.factory.Bar", {"length": 42}),
        "iron": ("tests.unit.factory.IronBar", {"length": 24}),
        "steel": ("tests.unit.factory.SteelBeam", {}),
    }

    # Factory sample values
    TEST_NAMED_FACTORY_NO_DEFAULT: NamedPluginConfig = {
        "iron": ("tests.unit.factory.IronBar", {"length": 24}),
        "steel": ("tests.unit.factory.SteelBeam", {}),
    }

    TEST_ALIAS_FACTORY: NamedPluginConfig = {
        "steel": ("tests.unit.factory.SteelBeam", {}),
        "metal": ("alias", {"name": "steel"}),
        # Bad entries
        "plastic": ("alias", {}),
        "nylon": ("alias", {"name": ""}),
        "polythene": ("alias", {"name": "plastic"}),
        "polypropylene": ("alias", {"name": "oil"}),
        # Circular
        "stone": ("alias", {"name": "marble"}),
        "marble": ("alias", {"name": "brick"}),
        "brick": ("alias", {"name": "stone"}),
    }

    # Config sample values
    TEST_NAMED_CONFIG: NamedConfig = {
        "default": {"length": 42, "foo": "bar"},
        "eek": {"length": 24, "foo": "bar"},
    }

    # Providers
    TEST_PROVIDERS: Sequence[str] = [
        "tests.unit.conf.helpers.test_providers_factories.ProviderBaseTest"
    ]
