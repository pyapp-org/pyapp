# Test only upper values are included
UPPER_VALUE = "foo"
lower_value = "bar"
mixed_VALUE = "eek"

# Helpful test placeholders.
SETTING_1 = 1
SETTING_2 = 2
SETTING_3 = 3
SETTING_4 = 4
SETTING_5 = 5

# Factory sample values
TEST_NAMED_FACTORY = {
    "default": ("tests.unit.factory.Bar", {"length": 42}),
    "iron": ("tests.unit.factory.IronBar", {"length": 24}),
    "steel": ("tests.unit.factory.SteelBeam", {}),
}

# Factory sample values
TEST_NAMED_FACTORY_NO_DEFAULT = {
    "iron": ("tests.unit.factory.IronBar", {"length": 24}),
    "steel": ("tests.unit.factory.SteelBeam", {}),
}

TEST_ALIAS_FACTORY = {
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
TEST_NAMED_CONFIG = {
    "default": {"length": 42, "foo": "bar"},
    "eek": {"length": 24, "foo": "bar"},
}

# Providers
TEST_PROVIDERS = ["tests.unit.conf.helpers.test_providers_factories.ProviderBaseTest"]
