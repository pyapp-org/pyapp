import datetime
from argparse import ArgumentError, ArgumentParser, Namespace
from enum import Enum, IntEnum, auto

import pytest
from pyapp.app import argument_actions


class TestKeyValueAction:
    def test_init__default_values(self):
        target = argument_actions.KeyValueAction(
            option_strings="--option", dest="options"
        )

        assert isinstance(target.default, dict)
        assert target.metavar == "KEY=VALUE"

    @pytest.mark.parametrize(
        "value, expected",
        (
            ("x=y", {"x": "y"}),
            ("x=1", {"x": "1"}),
            ("x=", {"x": ""}),
            ("x=a=b", {"x": "a=b"}),
            (("x=1", "y=2"), {"x": "1", "y": "2"}),
        ),
    )
    def test_call__valid(self, value, expected):
        parser = ArgumentParser()
        namespace = Namespace()
        target = argument_actions.KeyValueAction(
            option_strings="--option", dest="options"
        )

        target(parser, namespace, value)

        assert namespace.options == expected

    @pytest.mark.parametrize("value", ("", "x"))
    def test_call__invalid(self, value):
        parser = ArgumentParser()
        namespace = Namespace()
        target = argument_actions.KeyValueAction(
            option_strings="--option", dest="options"
        )

        with pytest.raises(ArgumentError):
            target(parser, namespace, value)


class Colour(Enum):
    Red = "red"
    Green = "green"
    Blue = "blue"


class IntColour(IntEnum):
    Red = auto()
    Green = auto()
    Blue = auto()


class TestEnumActions:
    @pytest.fixture
    def name_target(self):
        return argument_actions.EnumName(
            option_strings="--colour", dest="colour", type=Colour
        )

    @pytest.fixture
    def value_target(self):
        return argument_actions.EnumValue(
            option_strings="--colour", dest="colour", type=Colour
        )

    def test_init__name_choices(self, name_target):
        assert name_target.choices == ("Red", "Green", "Blue")

    def test_init__value_choices(self, value_target):
        assert value_target.choices == ("red", "green", "blue")

    def test_init__invalid_choices(self):
        with pytest.raises(ValueError, match="choices contains a non"):
            argument_actions.EnumName(
                option_strings="--colour",
                dest="colour",
                type=Colour,
                choices=(Colour.Blue, "Pink"),
            )

    def test_init__valid_choices(self):
        target = argument_actions.EnumName(
            option_strings="--colour",
            dest="colour",
            type=Colour,
            choices=(Colour.Blue, Colour.Red),
        )

        assert target.choices == ("Blue", "Red")

    def test_init__type_not_provided(self):
        with pytest.raises(ValueError, match="type must be assigned an Enum"):
            argument_actions.EnumName(option_strings="--colour", dest="colour")

    def test_init__type_not_an_enum(self):
        with pytest.raises(TypeError, match="type must be an Enum"):
            argument_actions.EnumName(
                option_strings="--colour", type=str, dest="colour"
            )

    def test_call__name_choices(self, name_target):
        parser = ArgumentParser()
        namespace = Namespace()
        name_target(parser, namespace, "Green")

        assert namespace.colour == Colour.Green

    def test_call__value_choices(self, value_target):
        parser = ArgumentParser()
        namespace = Namespace()
        value_target(parser, namespace, "blue")

        assert namespace.colour == Colour.Blue

    def test_call__with_int_enum(self):
        target = argument_actions.EnumName(
            option_strings="--colour", dest="colour", type=IntColour
        )
        parser = ArgumentParser()
        namespace = Namespace()

        target(parser, namespace, "Blue")

        assert namespace.colour == IntColour.Blue


class TestAppendEnumActions:
    @pytest.fixture
    def name_target(self):
        return argument_actions.AppendEnumName(
            option_strings="--colours", dest="colours", type=Colour
        )

    @pytest.fixture
    def value_target(self):
        return argument_actions.AppendEnumValue(
            option_strings="--colours", dest="colours", type=Colour
        )

    def test_call__name_choices(self, name_target):
        parser = ArgumentParser()
        namespace = Namespace()
        name_target(parser, namespace, "Green")
        name_target(parser, namespace, "Red")

        assert namespace.colours == [Colour.Green, Colour.Red]

    def test_call__value_choices(self, value_target):
        parser = ArgumentParser()
        namespace = Namespace()
        value_target(parser, namespace, "red")
        value_target(parser, namespace, "blue")

        assert namespace.colours == [Colour.Red, Colour.Blue]


class TestDateTimeActions:
    @pytest.mark.parametrize(
        "value, action, expected",
        (
            ("2022-10-03", argument_actions.DateAction, datetime.date(2022, 10, 3)),
            ("12:43:12", argument_actions.TimeAction, datetime.time(12, 43, 12)),
            (
                "2022-10-03t12:43:12",
                argument_actions.DateTimeAction,
                datetime.datetime(2022, 10, 3, 12, 43, 12),
            ),
            (
                "2022-10-03 12:43:12",
                argument_actions.DateTimeAction,
                datetime.datetime(2022, 10, 3, 12, 43, 12),
            ),
            (
                "2022-10-03T12:43:12",
                argument_actions.DateTimeAction,
                datetime.datetime(2022, 10, 3, 12, 43, 12),
            ),
        ),
    )
    def test_call__valid(self, value, action, expected):
        parser = ArgumentParser()
        namespace = Namespace()
        target = action(option_strings="--actual", dest="actual")

        target(parser, namespace, value)

        assert namespace.actual == expected
