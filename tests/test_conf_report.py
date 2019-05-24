import pytest

from tests.sample_app.__main__ import app

from pyapp.conf import report


@pytest.mark.parametrize("args", (("settings",), ("--nocolor", "settings")))
def test_run_report_from_app(args):
    app.dispatch(args=args)
