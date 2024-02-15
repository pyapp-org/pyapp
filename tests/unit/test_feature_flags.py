from unittest.mock import Mock

import pytest
from pyapp import feature_flags
from pyapp.conf import settings


class FeatureFlagsWrapper(feature_flags.FeatureFlags):
    pass


class TestFeatureFlags:
    @pytest.mark.parametrize(
        "flag, expected",
        (
            ("enable-a", True),
            ("Enable b", False),
            ("ENABLE_C", None),
        ),
    )
    def test_resolve_from_environment(self, monkeypatch, flag, expected):
        monkeypatch.setenv("PYAPP_FLAG_ENABLE_A", "On")
        monkeypatch.setenv("PYAPP_FLAG_ENABLE_B", "false")

        actual = feature_flags.DEFAULT._resolve_from_environment(flag)

        assert actual is expected

    @pytest.mark.parametrize(
        "flag, expected",
        (
            ("enable-a", True),
            ("Enable b", False),
            ("ENABLE_C", None),
        ),
    )
    def test_resolve_from_settings(self, flag, expected):
        with settings.modify() as patch:
            patch.FEATURE_FLAGS = {
                "enable-a": True,
                "Enable b": False,
            }

            actual = feature_flags.DEFAULT._resolve_from_settings(flag)

        assert actual is expected

    @pytest.mark.parametrize(
        "flag, expected",
        (
            ("enable-a", True),
            ("Enable b", True),
            ("Enable_C", True),
            ("Enable-D", False),
        ),
    )
    def test_resolve(self, monkeypatch, flag, expected):
        monkeypatch.setenv("PYAPP_FLAG_ENABLE_A", "On")
        monkeypatch.setenv("PYAPP_FLAG_ENABLE_B", "true")

        with settings.modify() as patch:
            patch.FEATURE_FLAGS = {
                "enable-b": False,
                "Enable_C": True,
            }

            actual = feature_flags.DEFAULT._resolve(flag, False)

        assert actual is expected

    def test_get__where_feature_flag_is_cached(self):
        target = FeatureFlagsWrapper()
        target._cache["EnableD"] = "Mock_Value"
        target._resolve = Mock(return_value="Mock_Value")

        actual = target.get("EnableD")

        assert actual == "Mock_Value"
        target._resolve.assert_not_called()

    def test_get__where_feature_flag_is_not_cached(self):
        target = FeatureFlagsWrapper()
        target._resolve = Mock(return_value="Mock_Value")

        actual = target.get("EnableD")

        assert actual == "Mock_Value"
        target._resolve.assert_called_once_with("EnableD", False)

    def test_set(self):
        target = feature_flags.FeatureFlags()

        target.set("EnableA", True)

        assert target._cache["EnableA"] is True

    @pytest.mark.parametrize(
        "option_a, option_b, state, expected",
        (
            ("A-Value", "B-Value", True, "A-Value"),
            ("A-Value", "B-Value", False, "B-Value"),
            (lambda: "A-Value", lambda: "B-Value", True, "A-Value"),
            (lambda: "A-Value", lambda: "B-Value", False, "B-Value"),
        ),
    )
    def test_a_or_b(self, option_a, option_b, state, expected):
        target = FeatureFlagsWrapper()
        target._get = Mock(return_value=state)

        actual = target.a_or_b("EnableE", option_a, option_b)

        assert actual == expected

    @pytest.mark.parametrize(
        "state, expected",
        (
            (True, "ValueA"),
            (False, None),
        ),
    )
    def test_if_enabled__where_return_is_default(self, state, expected):
        target = FeatureFlagsWrapper()
        target._get = Mock(return_value=state)

        @target.if_enabled("EnableF")
        def _sample(arg_a):
            return arg_a

        actual = _sample("ValueA")

        assert actual == expected

    @pytest.mark.parametrize(
        "state, expected",
        (
            (True, "ValueA"),
            (False, "ValueB"),
        ),
    )
    def test_if_enabled__where_return_is_customised(self, state, expected):
        target = FeatureFlagsWrapper()
        target._get = Mock(return_value=state)

        @target.if_enabled("EnableF", disabled_return="ValueB")
        def _sample(arg_a):
            return arg_a

        actual = _sample("ValueA")

        assert actual == expected

    def test_if_enabled__where_is_wrapped_correctly(self):
        target = FeatureFlagsWrapper()
        target._get = Mock(return_value=True)

        @target.if_enabled("FOO")
        def foo():
            """Sample"""

        assert foo.__doc__ == "Sample"
