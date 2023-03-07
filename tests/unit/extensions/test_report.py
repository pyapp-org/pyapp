import pytest
from pyapp.extensions import report
from pyapp.extensions.registry import ExtensionDetail

from tests.unit.sample_app.__main__ import app
from tests.unit.sample_ext import SampleExtension
from tests.unit.sample_ext_simple import SampleSimpleExtension


class MockFile:
    def __init__(self):
        self.lines = []

    def write(self, data):
        self.lines.append(data)


class TestExtensionReport:
    @pytest.fixture
    def extensions(self):
        return [
            ExtensionDetail(
                SampleExtension(), "SampleExtension", "Sample Extension", "1.1"
            ),
            ExtensionDetail(
                SampleSimpleExtension(),
                "SampleSimpleExtension",
                "Sample Simple Extension",
                "1.2",
            ),
        ]

    @pytest.mark.parametrize(
        "kwargs, expected",
        (
            ({"verbose": False, "no_color": False}, []),
            ({"verbose": True, "no_color": False}, []),
            ({"verbose": False, "no_color": True}, []),
            ({"verbose": True, "no_color": True}, []),
        ),
    )
    def test_output_result(self, extensions, kwargs, expected):
        f_out = MockFile()
        target = report.ExtensionReport(
            **kwargs, f_out=f_out, extension_registry=extensions
        )

        target.run()

        assert len(f_out.lines) == 2


@pytest.mark.parametrize(
    "args",
    (
        ("extensions",),
        ("extensions", "--verbose"),
        ("--nocolor", "extensions"),
        ("--nocolor", "extensions", "--verbose"),
    ),
)
def test_run_report_from_app(args, exit_code=4):
    app.dispatch(args=args)
