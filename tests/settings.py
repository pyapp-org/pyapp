# Test only upper values are included
UPPER_VALUE = 'foo'
lower_value = 'bar'
mixed_VALUE = 'eek'

# Helpful test placeholders.
SETTING_1 = 1
SETTING_2 = 2
SETTING_3 = 3
SETTING_4 = 4
SETTING_5 = 5

# Factory sample values
TEST_NAMED_FACTORY = {
    'default': (
        'tests.factory.Bar', {
            'length': 42
        },
    ),
    'iron': (
        'tests.factory.IronBar', {
            'length': 24
        },
    ),
    'steel': ('tests.factory.SteelBeam', {})
}

# Config sample values
TEST_NAMED_CONFIG = {
    'default': {
        'length': 42,
        'foo': 'bar'
    },
    'eek': {
        'length': 24,
        'foo': 'bar'
    }
}
