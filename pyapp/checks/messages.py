"""
Messages
"""
from __future__ import unicode_literals

from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


class CheckMessage(object):
    """
    Check message base class
    """
    def __init__(self, level, msg, hint=None, obj=None):
        """
        Messages returned from check functions.

        :param level: Importance level of message (based on logging levels)
        :type level: int
        :param msg: Description of issue identified by check. Note that this
            message will be word wrapped to 80 characters.
        :type msg: str
        :param hint: A hint on how to fix the issue (this can be either a
            single string or a list of strings that make up individual
            paragraphs. Note that any messages are word wrapped to 80 chars
            for display.
        :type hint: str | list(str)
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
