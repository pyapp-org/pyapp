from pyapp.documentation import settings


class TestSettingsDocumentor:
    def test_document(self, fixture_path):
        target = settings.SettingsDocumentor(
            fixture_path / "settings" / "default_settings.py"
        )

        target.process()
        actual = dict(target.discovered_settings)

        assert actual == {
            None: [
                (
                    "TOP_LEVEL_SETTING",
                    "bool",
                    False,
                    "This is a top level setting",
                ),
                (
                    "TOP_LEVEL_WITH_NO_COMMENT",
                    "int",
                    42,
                    None,
                ),
                (
                    "PATH_TO_SOME_FILE",
                    "str | Path",
                    "/path/to/some/file",
                    "Path to some file",
                ),
                (
                    "ENSURE_LAST_SETTING_DEFINED",
                    None,
                    False,
                    None,
                ),
            ],
            "FooSettings": [
                (
                    "FOO_SETTING",
                    "str",
                    "foo",
                    "A setting for Foo",
                ),
                (
                    "BAR_SETTING",
                    "int",
                    13,
                    "Another setting for Foo",
                ),
                (
                    "BAZ_SETTING",
                    "NamedConfig",
                    {"default": {"value": 1}},
                    None,
                ),
                (
                    "PLUGIN_SETTING",
                    "NamedPluginConfig",
                    {
                        "default": ["myapp.plugins.default", {}],
                    },
                    "Settings for plugin configuration.",
                ),
                (
                    "ENSURE_LAST_SETTING",
                    "bool",
                    True,
                    None,
                ),
            ],
        }
