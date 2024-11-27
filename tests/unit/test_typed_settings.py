from ..settings import MySettings, MyPrefixedSettings


def test_access_settings():
    assert MySettings.UPPER_VALUE == "foo"


def test_access_settings__where_setting_modified(patch_settings):
    patch_settings.UPPER_VALUE = "bar"

    assert MySettings.UPPER_VALUE == "bar"


def test_access_settings__where_settings_has_a_prefix(settings):
    assert settings.FOO_SETTING_1 == "my-prefixed-setting"
    assert MyPrefixedSettings.SETTING_1 == "my-prefixed-setting"
    assert MySettings.SETTING_1 == 1

