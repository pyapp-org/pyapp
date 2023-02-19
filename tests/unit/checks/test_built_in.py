from pyapp.checks import built_in
from pyapp.conf import settings


class TestSecurityChecks:
    def test_debug_enabled__check_defaults(self):
        result = built_in.debug_enabled(settings)

        # The default is for DEBUG to be False
        assert result is None

    def test_debug_enabled__warning_returned_if_enabled(self):
        with settings.modify() as patch:
            patch.DEBUG = True

            result = built_in.debug_enabled(settings)

        assert result == built_in.W001
