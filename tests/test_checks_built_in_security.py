from pyapp.conf import settings
from pyapp.checks.built_in import security


class TestSecurityChecks(object):
    def test_debug_enabled__check_defaults(self):
        result = security.debug_enabled(settings)

        # The default is for DEBUG to be False
        assert result is None

    def test_debug_enabled__warning_returned_if_enabled(self):
        with settings.modify() as patch:
            patch.DEBUG = True

            result = security.debug_enabled(settings)

        assert result == security.W001
