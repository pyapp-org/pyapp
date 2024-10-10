from pyapp import feature_flags


def test_settings_fixture(settings, patch_settings):
    patch_settings.FOO = "bar"

    assert settings.FOO == "bar"


def test_feature_flags_fixture(patch_feature_flags):
    patch_feature_flags["foo"] = True

    assert feature_flags.get("foo") is True


def test_check_registry(pytester):
    pytester.makepyfile(
        """
        from pyapp import checks
          
        def test_sample(check_registry):
            assert checks.registry is check_registry
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
