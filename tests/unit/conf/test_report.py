import pytest

from tests.unit.sample_app.__main__ import app


@pytest.mark.parametrize("args", (("settings",), ("--nocolor", "settings")))
def test_run_report_from_app(args):
    app.dispatch(args=args)
