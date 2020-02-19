import pytest

from pyapp.conf import report
from tests.sample_app.__main__ import app


@pytest.mark.parametrize("args", (("settings",), ("--nocolor", "settings")))
def test_run_report_from_app(args):
    app.dispatch(args=args)
