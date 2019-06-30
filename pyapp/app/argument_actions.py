"""
Argument Actions
~~~~~~~~~~~~~~~~

"""
from argparse import Action, ArgumentParser, ArgumentError, Namespace

from typing import Tuple, Union, Sequence

__all__ = ("KeyValueAction",)


class KeyValueAction(Action):
    """
    ArgParse action that accepts key/value pairs and appends them to a dictionary.

    Example of use::

        @app.command
        @argument("--option", action=KeyValueAction)
        def my_command(opts: Namespace):
            assert isinstance(opts.option, dict)

    """

    def __init__(self, **kwargs):
        kwargs.setdefault("metavar", "KEY=VALUE")
        kwargs.setdefault("default", {})
        super().__init__(**kwargs)

    def parse_value(self, value: str) -> Tuple[str, str]:
        values = value.split("=", 1)
        if len(values) != 2:
            raise ArgumentError(self, "Expected in the form KEY=VALUE")
        return values

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Union[Sequence[str], str],
        option_string: str = None,
    ):
        # Ensure dest exists
        try:
            items = getattr(namespace, self.dest)
        except AttributeError:
            items = {}
            setattr(namespace, self.dest, items)

        # Normalise string into a sequence
        if isinstance(values, str):
            values = (values,)

        # Parse values
        parse_value = self.parse_value
        items.update(parse_value(value) for value in values)
