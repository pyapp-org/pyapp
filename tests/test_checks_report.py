import pytest

from pyapp.conf import settings

from tests.sample_app.__main__ import app


@pytest.mark.parametrize('args', (
    ('checks',),
    ('checks', '--verbose'),
    ('--nocolor', 'checks'),
    ('--nocolor', 'checks', '--verbose'),
))
def test_run_report_from_app(args, exit_code=4):
    with settings.modify() as patch:
        patch.DEBUG = True

        with pytest.raises(SystemExit) as ex:
            app.dispatch(args=args)

        assert ex.value.code == exit_code
