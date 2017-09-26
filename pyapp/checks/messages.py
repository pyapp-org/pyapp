"""
Messages
"""
from __future__ import unicode_literals

from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, getLevelName

# Typing imports
from typing import Any, Union, List  # noqa

__all__ = (
    'CheckMessage',
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
    'Debug', 'Info', 'Warn', 'Error', 'Critical',
)


class CheckMessage(object):
    """
    Check message base class
    """
    def __init__(self, level, msg, hint=None, obj=None):
        # type: (int, str, Union[str, List[str]], Any) -> None
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
        self.hint = hint
        self.obj = obj

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            all(getattr(self, attr) == getattr(other, attr)
                for attr in ('level', 'msg', 'hint', 'obj'))
        )

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        if self.obj is None:
            obj = "?"
        else:
            obj = str(self.obj)
        hint = "\n\tHINT: {}".format(self.hint) if self.hint else ''
        return "{}: {}{}".format(obj, self.msg, hint)

    def __repr__(self):
        return "{}(level={!r}, msg={!r}, hint={!r}, obj={!r})".format(
            self.__class__.__name__, self.level, self.msg, self.hint, self.obj
        )

    @property
    def level_name(self):
        # type: () -> str
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
    def __init__(self, *args, **kwargs):
        super(Debug, self).__init__(DEBUG, *args, **kwargs)


class Info(CheckMessage):
    """
    Info check message
    """
    def __init__(self, *args, **kwargs):
        super(Info, self).__init__(INFO, *args, **kwargs)


class Warn(CheckMessage):
    """
    Warning check message
    """
    def __init__(self, *args, **kwargs):
        super(Warn, self).__init__(WARNING, *args, **kwargs)


class Error(CheckMessage):
    """
    Error check message
    """
    def __init__(self, *args, **kwargs):
        super(Error, self).__init__(ERROR, *args, **kwargs)


class Critical(CheckMessage):
    """
    Critical check message
    """
    def __init__(self, *args, **kwargs):
        super(Critical, self).__init__(CRITICAL, *args, **kwargs)
