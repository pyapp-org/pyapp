import pytest

import tests.sample_app
import tests.sample_app_simple.__main__
from pyapp.app import _key_help
from pyapp.app import argument
from pyapp.app import CliApplication
from pyapp.app.logging_formatter import ColourFormatter


@pytest.mark.parametrize("key, expected", (("FOO", "FOO [eek]"), ("BAR", "BAR")))
def test_key_help(monkeypatch, key, expected):
    monkeypatch.setenv("FOO", "eek")

    actual = _key_help(key)

    assert actual == expected


class TestCliApplication:
    def test_initialisation(self):
        target = CliApplication(tests.sample_app)

        assert target.root_module is tests.sample_app
        assert target.application_settings == "tests.sample_app.default_settings"
        assert len(target._handlers) == 3

    def test_initialisation__no_root(self):
        target = tests.sample_app_simple.__main__.app

        assert target.root_module is tests
        assert target.application_settings == "tests.default_settings"

    def test_initialisation_alternate_settings(self):
        target = CliApplication(
            tests.sample_app, application_settings="tests.runtime_settings"
        )

        assert target.application_settings == "tests.runtime_settings"

    def test_dispatch_args(self):
        closure = {}

        target = CliApplication(tests.sample_app)

        @target.command(name="sample")
        @argument("--foo", dest="foo")
        def sample_handler(opts):
            closure["opts"] = opts

        target.dispatch(args=("sample", "--foo", "bar"))

        assert closure["opts"].foo == "bar"

    def test_dispatch(self):
        target = tests.sample_app.__main__.app

        target.dispatch(args=("happy",))

    def test_dispatch__keyboard_interrupt(self):
        target = tests.sample_app.__main__.app

        with pytest.raises(SystemExit) as ex:
            target.dispatch(args=("cheeky",))

        assert ex.value.code == -2

    def test_dispatch__return_status(self):
        target = tests.sample_app.__main__.app

        with pytest.raises(SystemExit) as ex:
            target.dispatch(args=("sad",))

        assert ex.value.code == -2

    def test_dispatch__exception(self):
        target = tests.sample_app.__main__.app

        with pytest.raises(Exception) as ex:
            target.dispatch(args=("angry",))

        assert str(ex.value) == "Grrrr"

    def test_get_log_formatter__force_colour(self):
        target = tests.sample_app.__main__.app

        actual = target.get_log_formatter(True)

        assert isinstance(actual, ColourFormatter)

    def test_loading_logging(self):
        import logging

        target = CliApplication(
            tests.sample_app, application_settings="tests.sample_app.logging_settings"
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
        target = CliApplication(tests.sample_app, **kwargs)
        assert target.env_loglevel_key == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        (
            ({}, "PYAPP_SETTINGS"),
            ({"env_settings_key": "MYAPP_SETTINGS"}, "MYAPP_SETTINGS"),
        ),
    )
    def test_env_settings_key(self, kwargs, expected):
        target = CliApplication(tests.sample_app, **kwargs)
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
        target = CliApplication(tests.sample_app, **kwargs)
        assert str(target) == expected

    def test_repr(self):
        target = CliApplication(tests.sample_app, prog="testing")

        assert repr(target) == "CliApplication(<module tests.sample_app>)"
