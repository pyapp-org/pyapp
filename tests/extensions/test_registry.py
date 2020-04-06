import mock
import pytest

from pyapp.extensions.registry import ExtensionDetail
from pyapp.extensions.registry import ExtensionEntryPoints
from pyapp.extensions.registry import ExtensionRegistry
from pyapp.extensions.registry import pkg_resources
from tests.sample_ext import SampleExtension
from tests.sample_ext_simple import SampleSimpleExtension


class TestExtensionDetail:
    @pytest.fixture
    def target(self):
        return ExtensionDetail(
            SampleExtension(), "SampleExtension", "Sample Extension", "1.1"
        )

    @pytest.fixture
    def target_simple(self):
        return ExtensionDetail(
            SampleSimpleExtension(),
            "SampleSimpleExtension",
            "Sample Simple Extension",
            "1.2",
        )

    def test_default_settings(self, target: ExtensionDetail):
        assert target.default_settings == "tests.sample_ext.default_settings"

    def test_default_settings__absolute(self, target_simple: ExtensionDetail):
        assert target_simple.default_settings == "tests.sample_ext.default_settings"

    def test_checks_module(self, target: ExtensionDetail):
        assert target.checks_module == "tests.sample_ext.checks"

    def test_checks_module__absolute(self, target_simple: ExtensionDetail):
        assert target_simple.checks_module == "tests.sample_ext.checks"

    def test_register_commands(self, target: ExtensionDetail):
        target.register_commands("abc")

        assert target.extension.register_commands_called == "abc"

    def test_checks_module__not_defined(self, target_simple: ExtensionDetail):
        target_simple.register_commands("abc")

        assert target_simple.extension.register_commands_called is False

    def test_ready(self, target: ExtensionDetail):
        target.ready()

        assert target.extension.ready_called is True

    def test_ready__not_defined(self, target_simple: ExtensionDetail):
        target_simple.ready()

        assert target_simple.extension.ready_called is False


def _make_entry_point(name, project_name, version):
    mock_entry_point = mock.Mock()
    mock_entry_point.name = name
    mock_entry_point.dist.project_name = project_name
    mock_entry_point.dist.version = version
    mock_entry_point.resolve.return_value = "ExtensionInstance"
    return mock_entry_point


class TestExtensionEntryPoints:
    @pytest.fixture
    def patchentrypoints(self, monkeypatch):
        entry_points = (
            _make_entry_point("FooExtension", "foo-extension", "0.1.2"),
            _make_entry_point("BarExtension", "bar-extension", "3.2.1"),
        )

        mock_iter_entry_points = mock.Mock(return_value=entry_points)
        monkeypatch.setattr(pkg_resources, "iter_entry_points", mock_iter_entry_points)

    @pytest.fixture
    def target(self, patchentrypoints):
        return ExtensionEntryPoints()

    def test_entry_points(self, target: ExtensionEntryPoints):
        actual = [ep.name for ep in target._entry_points()]

        assert ["FooExtension", "BarExtension"] == actual

    def test_entry_points__with_white_list(self, patchentrypoints):
        target = ExtensionEntryPoints(white_list=("BarExtension",))

        actual = [ep.name for ep in target._entry_points()]

        assert ["BarExtension"] == actual

    def test_extensions(self, target: ExtensionEntryPoints):
        actual = list(target.extensions())

        assert [
            ExtensionDetail(
                "ExtensionInstance", "FooExtension", "foo-extension", "0.1.2"
            ),
            ExtensionDetail(
                "ExtensionInstance", "BarExtension", "bar-extension", "3.2.1"
            ),
        ] == actual

    def test_extensions__no_load(self, target: ExtensionEntryPoints):
        actual = list(target.extensions(False))

        assert [
            ExtensionDetail(None, "FooExtension", "foo-extension", "0.1.2"),
            ExtensionDetail(None, "BarExtension", "bar-extension", "3.2.1"),
        ] == actual


class TestExtensionRegistry:
    @pytest.fixture
    def target(self):
        return ExtensionRegistry(
            [
                ExtensionDetail(
                    SampleExtension(), "SampleExtension", "Sample Extension", "1.1"
                )
            ]
        )

    def test_load_from(self, target: ExtensionRegistry):
        target.load_from(
            [
                ExtensionDetail(
                    SampleSimpleExtension(),
                    "SampleSimpleExtension",
                    "Sample Simple Extension",
                    "1.2",
                )
            ]
        )

        assert len(target) == 2

    def test_register_commands(self, target: ExtensionRegistry):
        mock_extension = mock.Mock()
        target.append(
            ExtensionDetail(mock_extension, "MockExtension", "Mock Extension", "1.1")
        )

        target.register_commands("abc")

        mock_extension.register_commands.assert_called_with("abc")

    def test_ready(self, target: ExtensionRegistry):
        mock_extension = mock.Mock()
        target.append(
            ExtensionDetail(mock_extension, "MockExtension", "Mock Extension", "1.1")
        )

        target.ready()

        mock_extension.ready.assert_called()
