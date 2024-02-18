"""
PyApp Utils
~~~~~~~~~~~
"""

import importlib
import textwrap
from fnmatch import fnmatch
from typing import Any, Container, Sequence


def is_iterable(obj: Any) -> bool:
    """Determine if an object is iterable."""
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
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, cls):
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


# Alias to be consistent with Python.
cached_property = CachedProperty  # pylint: disable=invalid-name


def import_type(type_name: str) -> type:
    """Import a type from a fully qualified module+type name"""
    module_name, type_name = type_name.rsplit(".", 1)
    mod = importlib.import_module(module_name)
    return getattr(mod, type_name)


def wrap_text(
    text: str, width: int, *, indent: int = 0, padding: int = 1, line_sep: str = "\n"
) -> str:
    """Perform word wrapping on text

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
    return line_sep.join(f"{line}{' ' * (width - len(line))}" for line in lines)


TRUE_VALUES = ("TRUE", "T", "YES", "Y", "ON", "1")


def text_to_bool(value: Any, *, true_values: Container[str] = TRUE_VALUES) -> bool:
    """Resolve a string into a bool eg "yes" -> True"""
    if isinstance(value, str):
        return value.upper() in true_values
    return False


class AllowBlockFilter:
    """Filter for allow/block lists.

    Filter lists can be either plan strings or glob patterns.
    """

    def __init__(
        self,
        allow_list: Sequence[str] = None,
        block_list: Sequence[str] = None,
    ):
        """Initialise filter"""
        self.allow_list = allow_list
        self.block_list = block_list

    def __call__(self, value: str) -> bool:
        """Check if a value is allowed"""
        allow_list, block_list = self.allow_list, self.block_list

        if block_list is not None and any(
            fnmatch(value, pattern) for pattern in block_list
        ):
            return False

        if allow_list is not None:
            return any(fnmatch(value, pattern) for pattern in self.allow_list)

        return True
