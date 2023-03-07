from ..settings import MySettings


def test_access_settings():
    assert MySettings.UPPER_VALUE == "foo"


def test_access_settings__where_setting_modified(patch_settings):
    patch_settings.UPPER_VALUE = "bar"

    assert MySettings.UPPER_VALUE == "bar"
