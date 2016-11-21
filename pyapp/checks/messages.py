"""
Messages
"""

# Levels
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50


class CheckMessage(object):
    """
    Check message base class
    """
    def __init__(self, level, msg, hint=None, obj=None):
        assert isinstance(level, int), "The first argument should be level."
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
    def __init__(self, *args, **kwargs):
        super(Info, self).__init__(INFO, *args, **kwargs)


class Warn(CheckMessage):
    def __init__(self, *args, **kwargs):
        super(Warn, self).__init__(WARNING, *args, **kwargs)


class Error(CheckMessage):
    def __init__(self, *args, **kwargs):
        super(Error, self).__init__(ERROR, *args, **kwargs)


class Critical(CheckMessage):
    def __init__(self, *args, **kwargs):
        super(Critical, self).__init__(CRITICAL, *args, **kwargs)
