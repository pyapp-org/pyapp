from pyapp import testing


def test_settings_in_module():
    from pyapp.conf import base_settings

    actual = testing.settings_in_module(base_settings)

    assert actual == {
        "DEBUG",
        "LOG_LOGGERS",
        "LOG_HANDLERS",
        "LOGGING",
        "CHECK_LOCATIONS",
        "FEATURE_FLAGS",
        "FEATURE_FLAG_PREFIX",
    }
