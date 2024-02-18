from pyapp.documentation import settings


class TestSettingsDocumentor:
    def test_document(self, fixture_path):
        target = settings.SettingsCollection(
            fixture_path / "settings" / "default_settings.py"
        )

        target.process()

        assert target.settings == {
            None: settings.SettingDefGroup(
                None,
                [
                    settings.SettingDef(
                        "TOP_LEVEL_SETTING",
                        "bool",
                        False,
                        "This is a top level setting",
                    ),
                    settings.SettingDef(
                        "TOP_LEVEL_WITH_NO_COMMENT",
                        "int",
                        42,
                        None,
                    ),
                    settings.SettingDef(
                        "PATH_TO_SOME_FILE",
                        "str | Path",
                        "/path/to/some/file",
                        "Path to some file",
                    ),
                    settings.SettingDef(
                        "ENSURE_LAST_SETTING_DEFINED",
                        None,
                        False,
                        None,
                    ),
                ],
                None,
            ),
            "FooSettings": settings.SettingDefGroup(
                "FooSettings",
                [
                    settings.SettingDef(
                        "FOO_SETTING",
                        "str",
                        "foo",
                        "A setting for Foo",
                    ),
                    settings.SettingDef(
                        "BAR_SETTING",
                        "int",
                        13,
                        "Another setting for Foo",
                    ),
                    settings.SettingDef(
                        "BAZ_SETTING",
                        "NamedConfig",
                        {"default": {"value": 1}},
                        None,
                    ),
                    settings.SettingDef(
                        "PLUGIN_SETTING",
                        "NamedPluginConfig",
                        {
                            "default": ["myapp.plugins.default", {}],
                        },
                        "Settings for plugin configuration.",
                    ),
                    settings.SettingDef(
                        "ENSURE_LAST_SETTING",
                        "bool",
                        True,
                        None,
                    ),
                ],
                "Settings for Foo",
            ),
        }
        assert target.all_settings == settings.SettingDefGroup(
            None,
            [
                settings.SettingDef(
                    "TOP_LEVEL_SETTING",
                    "bool",
                    False,
                    "This is a top level setting",
                ),
                settings.SettingDef(
                    "TOP_LEVEL_WITH_NO_COMMENT",
                    "int",
                    42,
                    None,
                ),
                settings.SettingDef(
                    "PATH_TO_SOME_FILE",
                    "str | Path",
                    "/path/to/some/file",
                    "Path to some file",
                ),
                settings.SettingDef(
                    "ENSURE_LAST_SETTING_DEFINED",
                    None,
                    False,
                    None,
                ),
                settings.SettingDef(
                    "FOO_SETTING",
                    "str",
                    "foo",
                    "A setting for Foo",
                ),
                settings.SettingDef(
                    "BAR_SETTING",
                    "int",
                    13,
                    "Another setting for Foo",
                ),
                settings.SettingDef(
                    "BAZ_SETTING",
                    "NamedConfig",
                    {"default": {"value": 1}},
                    None,
                ),
                settings.SettingDef(
                    "PLUGIN_SETTING",
                    "NamedPluginConfig",
                    {
                        "default": ["myapp.plugins.default", {}],
                    },
                    "Settings for plugin configuration.",
                ),
                settings.SettingDef(
                    "ENSURE_LAST_SETTING",
                    "bool",
                    True,
                    None,
                ),
            ],
            None,
        )
