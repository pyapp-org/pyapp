import pytest

from pyapp.checks import messages


class TestCheckMessage(object):
    @pytest.mark.parametrize(('message_type', 'expected', 'is_serious'), (
        (messages.Debug, messages.DEBUG, False),
        (messages.Info, messages.INFO, False),
        (messages.Warn, messages.WARNING, False),
        (messages.Error, messages.ERROR, True),
        (messages.Critical, messages.CRITICAL, True),
    ))
    def test_level__from_message_overrides(self, message_type, expected, is_serious):
        instance = message_type('Foo')

        assert instance.level == expected
        assert instance.is_serious() == is_serious

    def test_eq__equal_to_self(self):
        target = messages.Debug("Debug")

        assert target == target

    def test_eq__equal_to_same_constructor_values(self):
        assert messages.Info("Info") == messages.Info("Info")

    def test_ne___not_equal_to_different_constructor_values(self):
        assert messages.Error("Error") != messages.Error("Error2")

    @pytest.mark.parametrize(('cls', 'msg', 'hint', 'obj', 'expected'), (
            (messages.Debug, 'Message', None, None, '?: Message'),
            (messages.Info, 'Message', 'Hint', None, '?: Message\n\tHINT: Hint'),
            (messages.Warn, 'Message', None, 'Obj', 'Obj: Message'),
            (messages.Error, 'Message', 'Hint', 'Obj', 'Obj: Message\n\tHINT: Hint'),
    ))
    def test_str(self, cls, msg, hint, obj, expected):
        actual = str(cls(msg, hint, obj))

        assert actual == expected

    @pytest.mark.parametrize(('cls', 'msg', 'hint', 'obj', 'expected'), (
            (messages.Debug, 'Message', None, None, "Debug(level=10, msg='Message', hint=None, obj=None)"),
            (messages.Info, 'Message', 'Hint', None, "Info(level=20, msg='Message', hint='Hint', obj=None)"),
            (messages.Warn, 'Message', None, 'Obj', "Warn(level=30, msg='Message', hint=None, obj='Obj')"),
            (messages.Error, 'Message', 'Hint', 'Obj', "Error(level=40, msg='Message', hint='Hint', obj='Obj')"),
    ))
    def test_repr(self, cls, msg, hint, obj, expected):
        actual = repr(cls(msg, hint, obj))

        assert actual == expected

