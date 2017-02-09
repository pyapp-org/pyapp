import pytest

from tests.sample_app.__main__ import app

from pyapp.extensions import report


@pytest.mark.parametrize('args', (
    ('extensions',),
    ('extensions', '--verbose'),
    ('--nocolor', 'extensions'),
    ('--nocolor', 'extensions', '--verbose'),
))
def test_run_report_from_app(args):
    app.dispatch(args=args)
