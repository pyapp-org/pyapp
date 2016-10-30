import pytest

from pyapp.checks import messages


class TestCheckMessage(object):
    @pytest.mark.parametrize(('message_type', 'expected', 'is_serious'), (
        (messages.Debug, messages.DEBUG, False),
        (messages.Info, messages.INFO, False),
        (messages.Warning, messages.WARNING, False),
        (messages.Error, messages.ERROR, True),
        (messages.Critical, messages.CRITICAL, True),
    ))
    def test_level__from_message_overrides(self, message_type, expected, is_serious):
        instance = message_type('Foo')

        assert instance.level == expected
        assert instance.is_serious() == is_serious
