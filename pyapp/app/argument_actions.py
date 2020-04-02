"""
Additional actions to handle common CLI situations.

Key/Value Arguments
~~~~~~~~~~~~~~~~~~~

.. autoclass:: KeyValueAction


Enum types
~~~~~~~~~~

.. autoclass:: EnumValue

.. autoclass:: EnumName

"""
from argparse import Action
from argparse import ArgumentError
from argparse import ArgumentParser
from argparse import Namespace
from enum import Enum
from typing import Sequence
from typing import Tuple
from typing import Union

__all__ = ("KeyValueAction",)


class KeyValueAction(Action):
    """
    Action that accepts key/value pairs and appends them to a dictionary.

    Example of use::

        @app.command
        @argument("--option", action=KeyValueAction)
        def my_command(args: Namespace):
            print(args.option)

    From CLI::

        > my_app m_command --option a=foo --option b=bar
        {'a': 'foo', 'b': 'bar'}

    """

    def __init__(self, **kwargs):
        kwargs.setdefault("metavar", "KEY=VALUE")
        kwargs.setdefault("default", {})
        super().__init__(**kwargs)

    def parse_value(self, value: str) -> Tuple[str, str]:
        """
        Parse a argument into a key/value pair
        """
        values = value.split("=", 1)
        if len(values) != 2:
            raise ArgumentError(self, "Expected in the form KEY=VALUE")
        return tuple(values)

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


class _EnumAction(Action):
    def __init__(self, **kwargs):
        enum = kwargs.pop("type")
        if enum is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")
        if not issubclass(enum, Enum):
            raise TypeError("type must be an Enum when using EnumAction")
        self._enum = enum

        if kwargs.get("choices") is None:
            kwargs["choices"] = self.get_choices()

        super().__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        enum = self.to_enum(values)
        setattr(namespace, self.dest, enum)

    def get_choices(self):
        """
        Get choices from the enum
        """
        raise NotImplementedError

    def to_enum(self, value):
        """
        Get enum from the supplied value.
        """
        raise NotImplementedError


class EnumValue(_EnumAction):
    """
    Action to use an Enum as the type of an argument. In this mode the Enum is
    reference by value.

    The choices are automatically generated for help.

    Example of use::

        class Colour(Enum):
            Red = "red"
            Green = "green"
            Blue = "blue"

        @app.command
        @argument("--colour", type=Colour, action=EnumValue)
        def my_command(args: Namespace):
            print(args.colour)

    From CLI::

        > my_app m_command --colour red
        Colour.Red

    """

    def get_choices(self):
        return tuple(e.value for e in self._enum)

    def to_enum(self, value):
        return self._enum(value)


class EnumName(_EnumAction):
    """
    Action to use an Enum as the type of an argument. In this mode the Enum is
    reference by name.

    The choices are automatically generated for help.

    Example of use::

        class Colour(Enum):
            Red = "red"
            Green = "green"
            Blue = "blue"

        @app.command
        @argument("--colour", type=Colour, action=EnumName)
        def my_command(args: Namespace):
            print(args.colour)

    From CLI::

        > my_app m_command --colour Red
        Colour.Red

    """

    def get_choices(self):
        return tuple(e.name for e in self._enum)

    def to_enum(self, value):
        return self._enum[value]
