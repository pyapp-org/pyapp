"""
Additional "types" to handle common CLI situations.

.. autoclass:: RegexType

"""
import argparse
import re


class RegexType:
    """
    Factory for validating string options against a regular expression.

    Instances of RegexType are typically passed as type= arguments to the
    ArgumentParser add_argument() method or pyApp argument decorator.

    :param regex: Regular expression string (or pre-compiled expression)
    :param message: Optional message if validation fails, defaults to a simple
        fallback.

    Example of use::

        @app.command
        @argument("--alpha", type=RegexType(r"[a-z]+"))
        def my_command(args: Namespace):
            print(args.option)

    From CLI::

        > my_app m_command --alpha abc
        abc

    .. versionadded:: 4.2

    """

    def __init__(self, regex, message: str = None):
        self._re = re.compile(regex)
        self._message = message or f"Value does not match {self._re.pattern!r}"

    def __call__(self, string):
        if not self._re.search(string):
            raise argparse.ArgumentTypeError(self._message)
        return string
