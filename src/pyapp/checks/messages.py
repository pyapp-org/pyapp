"""
Messages
"""

from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING, getLevelName
from traceback import format_exc
from typing import Any

__all__ = (
    "CheckMessage",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "Debug",
    "Info",
    "Warn",
    "Error",
    "Critical",
    "UnhandledException",
)


class CheckMessage:
    """
    Check message base class
    """

    __slots__ = ("level", "msg", "hint", "obj")

    def __init__(
        self,
        level: int,
        msg: str,
        hint: str = None,
        obj: Any = None,
    ):
        """
        Messages returned from check functions.

        :param level: Importance level of message (based on logging levels)
        :param msg: Description of issue identified by check. Note that this
            message will be word wrapped to 80 characters.
        :param hint: A hint on how to fix the issue (this can be either a
            single string or a list of strings that make up individual
            paragraphs. Note that any messages are word wrapped to 80 chars
            for display.
        :param obj: An object this message relates to (useful in the case of
            multiple database connections for example).

        """
        self.level = level
        self.msg = msg
        self.obj = obj
        self.hint = hint

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return all(
                getattr(self, attr) == getattr(other, attr)
                for attr in ("level", "msg", "hint", "obj")
            )
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __str__(self) -> str:
        obj = "?" if self.obj is None else str(self.obj)
        hint = f"\n\tHINT: {self.hint}" if self.hint else ""
        return f"{obj}: {self.msg}{hint}"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"msg={self.msg!r}, "
            f"hint={self.hint!r}, "
            f"obj={self.obj!r})"
        )

    @property
    def level_name(self) -> str:
        """
        Level as a string.
        """
        return getLevelName(self.level)

    def is_serious(self, level=ERROR):
        """
        Is this message a serious message?
        """
        return self.level >= level


class Debug(CheckMessage):
    """
    Debug check message
    """

    __slots__ = ()

    def __init__(
        self,
        msg: str,
        hint: str = None,
        obj: Any = None,
    ):
        super().__init__(DEBUG, msg, hint, obj)


class Info(CheckMessage):
    """
    Info check message
    """

    __slots__ = ()

    def __init__(
        self,
        msg: str,
        hint: str = None,
        obj: Any = None,
    ):
        super().__init__(INFO, msg, hint, obj)


class Warn(CheckMessage):
    """
    Warning check message
    """

    __slots__ = ()

    def __init__(
        self,
        msg: str,
        hint: str = None,
        obj: Any = None,
    ):
        super().__init__(WARNING, msg, hint, obj)


class Error(CheckMessage):
    """
    Error check message
    """

    __slots__ = ()

    def __init__(
        self,
        msg: str,
        hint: str = None,
        obj: Any = None,
    ):
        super().__init__(ERROR, msg, hint, obj)


class Critical(CheckMessage):
    """
    Critical check message
    """

    __slots__ = ()

    def __init__(
        self,
        msg: str,
        hint: str = None,
        obj: Any = None,
    ):
        super().__init__(CRITICAL, msg, hint, obj)


class UnhandledException(CheckMessage):
    """
    Special case of error message for unhandled exceptions
    """

    def __init__(
        self,
        msg: str = None,
        hint: str = None,
        obj: Any = None,
    ):
        super().__init__(ERROR, msg or "Unhandled Exception", hint or format_exc(), obj)
