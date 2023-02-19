import pytest
from pyapp.checks import messages


def exception_check():
    raise RuntimeError("Didn't see that one!")


class TestCheckMessage:
    @pytest.mark.parametrize(
        ("message_type", "expected", "is_serious"),
        (
            (messages.Debug, messages.DEBUG, False),
            (messages.Info, messages.INFO, False),
            (messages.Warn, messages.WARNING, False),
            (messages.Error, messages.ERROR, True),
            (messages.Critical, messages.CRITICAL, True),
        ),
    )
    def test_level__from_message_overrides(self, message_type, expected, is_serious):
        instance = message_type("Foo")

        assert instance.level == expected
        assert instance.is_serious() == is_serious

    def test_eq__equal_to_self(self):
        target = messages.Debug("Debug")

        assert target == target

    def test_eq__equal_to_same_constructor_values(self):
        assert messages.Info("Info") == messages.Info("Info")

    def test_eq__unknown_type(self):
        assert messages.Info("Info") != 123

    def test_ne___not_equal_to_different_constructor_values(self):
        assert messages.Error("Error") != messages.Error("Error2")

    @pytest.mark.parametrize(
        ("cls", "msg", "hint", "obj", "expected"),
        (
            (messages.Debug, "Message", None, None, "?: Message"),
            (messages.Info, "Message", "Hint", None, "?: Message\n\tHINT: Hint"),
            (messages.Warn, "Message", None, "Obj", "Obj: Message"),
            (messages.Error, "Message", "Hint", "Obj", "Obj: Message\n\tHINT: Hint"),
        ),
    )
    def test_str(self, cls, msg, hint, obj, expected):
        actual = str(cls(msg, hint, obj))

        assert actual == expected

    @pytest.mark.parametrize(
        ("cls", "msg", "hint", "obj", "expected"),
        (
            (
                messages.Debug,
                "Message",
                None,
                None,
                "Debug(msg='Message', hint=None, obj=None)",
            ),
            (
                messages.Info,
                "Message",
                "Hint",
                None,
                "Info(msg='Message', hint='Hint', obj=None)",
            ),
            (
                messages.Warn,
                "Message",
                None,
                "Obj",
                "Warn(msg='Message', hint=None, obj='Obj')",
            ),
            (
                messages.Error,
                "Message",
                "Hint",
                "Obj",
                "Error(msg='Message', hint='Hint', obj='Obj')",
            ),
        ),
    )
    def test_repr(self, cls, msg, hint, obj, expected):
        actual = repr(cls(msg, hint, obj))

        assert actual == expected

    def test_exc_info(self):
        try:
            exception_check()
        except Exception:
            target = messages.UnhandledException()

        assert (target.level_name, target.msg) == ("ERROR", "Unhandled Exception")
        assert target.hint.startswith("Traceback (most recent call last):")
        assert target.hint.endswith("RuntimeError: Didn't see that one!\n")
