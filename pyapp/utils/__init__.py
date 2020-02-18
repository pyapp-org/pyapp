"""
PyApp Utils
~~~~~~~~~~~
"""
import importlib
import textwrap
from typing import Any


def is_iterable(obj: Any) -> bool:
    """
    Determine if an object is iterable.
    """
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


class CachedProperty:
    """
    A property that is only computed once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property. (From bottle)
    """

    def __init__(self, func):
        self.__doc__ = getattr(func, "__doc__")
        self.func = func

    def __get__(self, obj, cls):
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


# Alias to be consistent with Python.
cached_property = CachedProperty  # pylint: disable=invalid-name


def import_type(type_name: str) -> type:
    """
    Import a type from a fully qualified module+type name
    """
    module_name, type_name = type_name.rsplit(".", 1)
    mod = importlib.import_module(module_name)
    return getattr(mod, type_name)


def wrap_text(
    text: str, width: int, *, indent: int = 0, padding: int = 1, line_sep: str = "\n"
) -> str:
    """
    Perform word wrapping on text

    :param text: Text to wrap.
    :param width: Width of text to wrap
    :param indent: Size of text indent.
    :param padding: On the start and end of lines
    :param line_sep: Line separator

    """
    indent = " " * indent
    lines = textwrap.wrap(
        text, width - (padding * 2), initial_indent=indent, subsequent_indent=indent
    )
    return line_sep.join(f"{l}{' ' * (width - len(l))}" for l in lines)
