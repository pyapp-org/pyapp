from argparse import ArgumentError
from argparse import ArgumentParser
from argparse import Namespace
from enum import Enum

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
