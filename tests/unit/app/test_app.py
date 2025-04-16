import builtins

import pytest
from pyapp import app, feature_flags
from pyapp.app import CliApplication, _key_help, argument
from pyapp.app.logging_formatter import ColourFormatter

import tests.unit.sample_app
import tests.unit.sample_app_simple


@pytest.mark.parametrize("key, expected", (("FOO", "FOO [eek]"), ("BAR", "BAR")))
def test_key_help(monkeypatch, key, expected):
    monkeypatch.setenv("FOO", "eek")

    actual = _key_help(key)

    assert actual == expected


class TestCliApplication:
    def test_initialisation(self):
        target = CliApplication(tests.unit.sample_app)

        assert target.root_module is tests.unit.sample_app
        assert target.application_settings == "tests.unit.sample_app.default_settings"
        assert len(target._handlers) == 3

    def test_initialisation__no_root(self):
        target = tests.unit.sample_app_simple.app

        assert target.root_module is tests
        assert target.application_settings == "tests.default_settings"

    def test_initialisation_alternate_settings(self):
        target = CliApplication(
            tests.unit.sample_app, application_settings="tests.unit.runtime_settings"
        )

        assert target.application_settings == "tests.unit.runtime_settings"

    def test_dispatch_args(self):
        closure = {}

        target = CliApplication(tests.unit.sample_app)

        @target.command(name="sample")
        @argument("--foo", dest="foo")
        def sample_handler(opts):
            closure["opts"] = opts

        target.dispatch(args=("sample", "--foo", "bar"))

        assert closure["opts"].foo == "bar"

    def test_dispatch(self):
        target = tests.unit.sample_app.__main__.app

        target.dispatch(args=("happy",))

    def test_dispatch__keyboard_interrupt(self):
        target = tests.unit.sample_app.__main__.app

        with pytest.raises(SystemExit) as ex:
            target.dispatch(args=("cheeky",))

        assert ex.value.code == 2

    def test_dispatch__return_status(self):
        target = tests.unit.sample_app.__main__.app

        with pytest.raises(SystemExit) as ex:
            target.dispatch(args=("sad",))

        assert ex.value.code == -2

    def test_dispatch__exception(self):
        target = tests.unit.sample_app.__main__.app

        with pytest.raises(Exception) as ex:
            target.dispatch(args=("angry",))

        assert str(ex.value) == "Grrrr"

    def test_dispatch__plain_group(self):
        target = tests.unit.sample_app.__main__.app

        with pytest.raises(SystemExit) as ex:
            target.dispatch(args=("plain", "sample"))

        assert ex.value.code == 1324

    def test_dispatch__class_group_static_function(self):
        target = tests.unit.sample_app.__main__.app

        with pytest.raises(SystemExit) as ex:
            target.dispatch(args=("class", "static"))

        assert ex.value.code == 1332

    def test_dispatch__class_group_with_non_static_function(self):
        target = tests.unit.sample_app.__main__.app

        with pytest.raises(SystemExit) as ex:
            target.dispatch(args=("class", "non-static", "2"))

        assert ex.value.code == 1350

    def test_dispatch__set_feature_flags__where_no_flag_set(self):
        target = tests.unit.sample_app.__main__.app
        feature_flags.DEFAULT._cache.clear()

        with pytest.raises(SystemExit) as ex:
            target.dispatch(args=("undecided",))

        assert ex.value.code == 30

    def test_dispatch__set_feature_flags__where_happy_enabled(self):
        target = tests.unit.sample_app.__main__.app
        feature_flags.DEFAULT._cache.clear()

        with pytest.raises(SystemExit) as ex:
            target.dispatch(
                args=(
                    "--enable-flag",
                    "happy",
                    "undecided",
                )
            )

        assert ex.value.code == 10

    def test_dispatch__set_feature_flags__where_sad_disabled(self):
        target = tests.unit.sample_app.__main__.app
        feature_flags.DEFAULT._cache.clear()

        with pytest.raises(SystemExit) as ex:
            target.dispatch(
                args=(
                    "--disable-flag",
                    "sad",
                    "undecided",
                )
            )

        assert ex.value.code == 20

    def test_get_log_formatter__force_colour(self):
        target = tests.unit.sample_app.__main__.app

        actual = target.get_log_formatter(True)

        assert isinstance(actual, ColourFormatter)

    def test_loading_logging(self):
        import logging

        target = CliApplication(
            tests.unit.sample_app,
            application_settings="tests.unit.sample_app.logging_settings",
        )

        target.dispatch(args=("--log-level", "WARN", "settings"))
        assert logging.root.level == logging.WARN

    @pytest.mark.parametrize(
        "kwargs, expected",
        (
            ({}, "PYAPP_LOGLEVEL"),
            ({"env_loglevel_key": "MYAPP_LOGLEVEL"}, "MYAPP_LOGLEVEL"),
        ),
    )
    def test_env_loglevel_key(self, kwargs, expected):
        target = CliApplication(tests.unit.sample_app, **kwargs)
        assert target.env_loglevel_key == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        (
            ({}, "PYAPP_SETTINGS"),
            ({"env_settings_key": "MYAPP_SETTINGS"}, "MYAPP_SETTINGS"),
        ),
    )
    def test_env_settings_key(self, kwargs, expected):
        target = CliApplication(tests.unit.sample_app, **kwargs)
        assert target.env_settings_key == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        (
            ({"prog": "testing"}, "testing version 1.2.3"),
            (
                {"prog": "testing", "description": "This is a test"},
                "testing version 1.2.3 - This is a test",
            ),
        ),
    )
    def test_summary(self, kwargs, expected):
        target = CliApplication(tests.unit.sample_app, **kwargs)
        assert str(target) == expected

    def test_repr(self):
        target = CliApplication(tests.unit.sample_app, prog="testing")

        assert repr(target) == "CliApplication(<module tests.unit.sample_app>)"

    def test_execution_policy__where_non_root(self, monkeypatch):
        monkeypatch.setattr(app, "is_root_user", lambda: False)

        CliApplication(tests.unit.sample_app)

    def test_execution_policy__where_root_user_and_deny(self, monkeypatch, capsys):
        monkeypatch.setattr(app, "is_root_user", lambda: True)

        with pytest.raises(SystemExit):
            CliApplication(tests.unit.sample_app, root_execution_policy=app.ExecutionPolicy.Deny)

        captured = capsys.readouterr()
        assert captured.err.startswith("Execution denied")

    def test_execution_policy__where_root_user_and_warning(self, monkeypatch, capsys):
        monkeypatch.setattr(app, "is_root_user", lambda: True)

        CliApplication(
            tests.unit.sample_app, root_execution_policy=app.ExecutionPolicy.Warn
        )

        captured = capsys.readouterr()
        assert captured.err.startswith("Warning! Executing as")

    def test_execution_policy__where_root_user_and_confirm_true(
        self, monkeypatch, capsys
    ):
        monkeypatch.setattr(app, "is_root_user", lambda: True)
        monkeypatch.setattr(builtins, "input", lambda x: "y")

        CliApplication(
            tests.unit.sample_app, root_execution_policy=app.ExecutionPolicy.Confirm
        )

        captured = capsys.readouterr()
        assert captured.err.startswith("Warning! Executing as")

    def test_execution_policy__where_root_user_and_confirm_false(
        self, monkeypatch, capsys
    ):
        monkeypatch.setattr(app, "is_root_user", lambda: True)
        monkeypatch.setattr(builtins, "input", lambda x: "")

        with pytest.raises(SystemExit):
            CliApplication(
                tests.unit.sample_app, root_execution_policy=app.ExecutionPolicy.Confirm
            )

        captured = capsys.readouterr()
        assert captured.err.startswith("Warning! Executing as")

    def test_execution_policy__where_root_user_env_override(self, monkeypatch):
        monkeypatch.setattr(app, "is_root_user", lambda: True)
        monkeypatch.setenv("PYAPP_ROOT_EXECUTION_POLICY", "allow")

        CliApplication(tests.unit.sample_app)

    def test_execution_policy__where_root_user_env_override_is_invalid(
        self, monkeypatch
    ):
        monkeypatch.setattr(app, "is_root_user", lambda: True)
        monkeypatch.setenv("PYAPP_ROOT_EXECUTION_POLICY", "boo")

        with pytest.raises(SystemExit):
            CliApplication(tests.unit.sample_app, root_execution_policy=app.ExecutionPolicy.Deny)

    def test_execution_policy__where_root_user_with_custom_environment_override(
        self, monkeypatch, capsys
    ):
        monkeypatch.setattr(app, "is_root_user", lambda: True)
        monkeypatch.setenv("MY_APP_ROOT_EXECUTION_POLICY", "warn")

        CliApplication(
            tests.unit.sample_app,
            env_root_execution_policy_key="MY_APP_ROOT_EXECUTION_POLICY",
        )

        captured = capsys.readouterr()
        assert captured.err.startswith("Warning! Executing as")
