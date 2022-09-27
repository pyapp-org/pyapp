def test_settings_fixture(pytester):
    pytester.makepyfile(
        """
        def test_sample(patch_settings):
            assert patch_settings.FOO == "bar"
    """
    )

    result = pytester.runpytest()
    assert result.ret == 1
