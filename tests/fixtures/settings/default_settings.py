"""Sample default settings file with various settings for testing documentation."""
from pathlib import Path
from typing import Union

from pyapp.typed_settings import NamedConfig, NamedPluginConfig, SettingsDef

INCLUDE_SETTINGS = ["myapp.plugins.default", "myapp.plugins.extra"]

not_a_setting = "Just a random constant."
not_a_setting_either: str = "But with a type!"

TOP_LEVEL_SETTING: bool = False
"""This is a top level setting"""

TOP_LEVEL_WITH_NO_COMMENT: int = 42


class FooSettings(SettingsDef):
    """Settings for Foo"""

    FOO_SETTING: str = "foo"
    """A setting for Foo"""

    BAR_SETTING: int = 13
    """Another setting for Foo"""

    BAZ_SETTING: NamedConfig = {
        "default": {"value": 1},
    }

    PLUGIN_SETTING: NamedPluginConfig = {
        "default": ("myapp.plugins.default", {}),
    }
    """Settings for plugin configuration."""

    ENSURE_LAST_SETTING: bool = True


PATH_TO_SOME_FILE: Union[str, Path] = "/path/to/some/file"
"""Path to some file"""


class RandomClass:
    NOT_ACTUALLY_A_SETTING = "But a class attribute"


ENSURE_LAST_SETTING_DEFINED = False
