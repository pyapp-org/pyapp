"""
Additional actions to handle common CLI situations.

Key/Value Arguments
~~~~~~~~~~~~~~~~~~~

.. autoclass:: KeyValueAction


Enum types
~~~~~~~~~~

.. autoclass:: EnumValue

.. autoclass:: EnumName

.. autoclass:: AppendEnumValue

.. autoclass:: AppendEnumName


Date and Time types
~~~~~~~~~~~~~~~~~~~

.. autoclass:: DateAction

.. autoclass:: TimeAction

.. autoclass:: DateTimeAction

"""

from argparse import Action, ArgumentError, ArgumentParser, Namespace
from datetime import date, datetime, time
from enum import Enum
from typing import Any, Callable, Dict, Sequence, Tuple, Type, Union

__all__ = (
    "KeyValueAction",
    "EnumValue",
    "EnumName",
    "EnumNameList",
    "AppendEnumValue",
    "AppendEnumName",
    "DateAction",
    "TimeAction",
    "DateTimeAction",
    "TYPE_ACTIONS",
)


class KeyValueAction(Action):
    """
    Action that accepts key/value pairs and appends them to a dictionary.

    Example of use::

        @app.command
        def my_command(options: Mapping[str, str]):
            print(options)

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
        """Parse an argument into a key/value pair"""
        key, part, value = value.partition("=")
        if not part:
            raise ArgumentError(self, "Expected in the form KEY=VALUE")
        return key, value

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
        enum = kwargs.pop("type", None)
        if enum is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")
        if not issubclass(enum, Enum):
            raise TypeError("type must be an Enum when using EnumAction")
        self._enum = enum

        choices = kwargs.get("choices")
        if choices:
            # Ensure all choices are from the enum
            try:
                outcome = all(c in enum for c in choices)
            except TypeError:
                # This path is for Python 3.8+ that does type checks in Enum.__contains__
                outcome = False

            if not outcome:
                raise ValueError(f"choices contains a non {enum} entry")

        else:
            choices = enum
        kwargs["choices"] = self.get_choices(choices)

        super().__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        enum = self.to_enum(values)
        setattr(namespace, self.dest, enum)

    def get_choices(self, choices: Union[Enum, Sequence[Enum]]):
        """
        Get choices from the enum
        """
        raise NotImplementedError  # pragma: no cover

    def to_enum(self, value):
        """
        Get enum from the supplied value.
        """
        raise NotImplementedError  # pragma: no cover


class EnumValue(_EnumAction):
    """
    Action to use an Enum as the type of an argument. In this mode the Enum is
    referenced by value.

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

    .. versionadded:: 4.2

    """

    def get_choices(self, choices: Union[Enum, Sequence[Enum]]):
        return tuple(e.value for e in choices)

    def to_enum(self, value):
        return self._enum(value)


class EnumName(_EnumAction):
    """
    Action to use an Enum as the type of an argument. In this mode the Enum is
    referenced by name.

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

    .. versionadded:: 4.2

    """

    def get_choices(self, choices: Union[Enum, Sequence[Enum]]):
        return tuple(e.name for e in choices)

    def to_enum(self, value):
        return self._enum[value]


def _copy_items(items):
    """
    Extracted from argparse
    """
    if items is None:
        return []

    # The copy module is used only in the 'append' and 'append_const'
    # actions, and it is needed only when the default value isn't a list.
    # Delay its import for speeding up the common case.
    if isinstance(items, list):
        return items[:]

    import copy  # pylint: disable=import-outside-toplevel

    return copy.copy(items)


class _AppendEnumActionMixin(_EnumAction):
    """
    Mixin to support appending enum items
    """

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = _copy_items(items)
        enum = self.to_enum(values)
        items.append(enum)
        setattr(namespace, self.dest, items)

    def get_choices(self, choices: Union[Enum, Sequence[Enum]]):
        """
        Get choices from the enum
        """
        raise NotImplementedError  # pragma: no cover

    def to_enum(self, value):
        """
        Get enum from the supplied value.
        """
        raise NotImplementedError  # pragma: no cover


class AppendEnumValue(EnumValue, _AppendEnumActionMixin):
    """
    Action to use an Enum as the type of an argument and to accept multiple
    enum values. In this mode the Enum is referenced by value.

    The choices are automatically generated for help.

    Example of use::

        class Colour(Enum):
            Red = "red"
            Green = "green"
            Blue = "blue"

        @app.command
        @argument("--colours", type=Colour, action=AppendEnumValue)
        def my_command(args: Namespace):
            print(args.colour)

        # Or using typing definition

        @app.command
        def my_command(*, colours: Sequence[Colour]):
            print(colours)

    From CLI::

        > my_app m_command --colour red --colour blue
        [Colour.Red, Colour.Blue]

    .. versionadded:: 4.9

    """


class AppendEnumName(EnumName, _AppendEnumActionMixin):
    """
    Action to use an Enum as the type of an argument and to accept multiple
    enum values. In this mode the Enum is referenced by name.

    The choices are automatically generated for help.

    Example of use::

        class Colour(Enum):
            Red = "red"
            Green = "green"
            Blue = "blue"

        @app.command
        @argument("--colours", type=Colour, action=AppendEnumName)
        def my_command(args: Namespace):
            print(args.colour)

    From CLI::

        > my_app m_command --colour Red --colour Blue
        [Colour.Red, Colour.Blue]

    .. versionadded:: 4.9

    """


EnumNameList = AppendEnumName


class _DateTimeAction(Action):
    """DateTime types."""

    parser: Callable[[str], Any]

    def __call__(self, parser, namespace, values, option_string=None):
        value = self.parser(values)
        setattr(namespace, self.dest, value)


class DateAction(_DateTimeAction):
    """Parse ISO date string."""

    parser = date.fromisoformat


class TimeAction(_DateTimeAction):
    """Parse ISO time string."""

    parser = time.fromisoformat


class DateTimeAction(_DateTimeAction):
    """Parse ISO datetime string."""

    parser = datetime.fromisoformat


TYPE_ACTIONS: Dict[type, Type[Action]] = {
    date: DateAction,
    time: TimeAction,
    datetime: DateTimeAction,
}
