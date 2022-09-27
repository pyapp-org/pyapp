import pytest
from pyapp.conf import settings

import tests.unit.sample_app_simple
from tests.unit.sample_app.__main__ import app


@pytest.mark.parametrize(
    "args",
    (
        ("checks",),
        ("checks", "--verbose"),
        ("checks", "--table"),
        ("--nocolor", "checks"),
        ("--nocolor", "checks", "--verbose"),
        ("--checks", "extensions", "--verbose"),
    ),
)
def test_run_report_from_app(args, exit_code=4):
    with settings.modify() as patch:
        patch.DEBUG = True

        with pytest.raises(SystemExit) as ex:
            app.dispatch(args=args)

        assert ex.value.code == exit_code


@pytest.mark.parametrize(
    "args",
    (
        ("checks",),
        ("checks", "--verbose"),
        ("checks", "--table"),
        ("--nocolor", "checks"),
        ("--nocolor", "checks", "--verbose"),
    ),
)
def test_run_report_from_simple_app(monkeypatch, args, exit_code=4):
    monkeypatch.setattr(tests.unit.sample_app_simple.app, "application_settings", None)
    monkeypatch.setattr(
        tests.unit.sample_app_simple.app, "application_checks", "__main__.checks"
    )

    with settings.modify() as patch:
        patch.DEBUG = True

        with pytest.raises(SystemExit) as ex:
            tests.unit.sample_app_simple.app.dispatch(args=args)

        assert ex.value.code == exit_code
