import pytest

from pyapp.extensions import report
from pyapp.extensions.registry import ExtensionDetail
from tests.sample_ext import SampleExtension
from tests.sample_ext_simple import SampleSimpleExtension


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
