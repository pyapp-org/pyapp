import argparse
from argparse import FileType
from enum import Enum
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union
from unittest import mock

import pytest

from pyapp.app import CommandOptions
from pyapp.app.argument_actions import EnumName
from pyapp.app.argument_actions import KeyValueAction
from pyapp.app.arguments import Arg
from pyapp.app.arguments import CommandProxy


def expected_args(*args):
    """
    Decorator to apply args expected to be extracted
    """

    def _wrapper(func):
        func.expected_args = list(args)
        return func

    return _wrapper


def call_args(*args: str, expected):
    """
    Decorator to provide a incoming arguments and the expected response
    """

    def _wrapper(func):
        func.call_args = (args, expected)
        return func

    return _wrapper


class Colour(Enum):
    Red = "red"
    Green = "green"


@expected_args()
def func_compatible_1(opts):
    return opts


@expected_args()
def func_compatible_2(args: CommandOptions):
    return args


@expected_args(mock.call("--arg-1", type=int, default=42))
def func_compatible_3(opts: CommandOptions, *, arg_1: int = Arg(default=42)):
    return opts, arg_1


@expected_args(mock.call("--arg-1", type=int, default=42))
def func_compatible_4(*, arg_1: int = Arg(default=42), args: CommandOptions):
    return arg_1, args


@expected_args()
def func_sample_01():
    pass


@expected_args(mock.call("ARG1", type=int))
@call_args("42", expected=42)
def func_sample_02(arg1: int):
    return arg1


@expected_args(
    mock.call("ARG1", type=str), mock.call("--arg2", type=str, default="foo"),
)
@call_args("42", expected=("42", "foo"))
def func_sample_03(arg1: str, *, arg2: str = "foo"):
    return arg1, arg2


@expected_args(
    mock.call("ARG1", type=str), mock.call("--arg2", action="store_true"),
)
@call_args("42", "--arg2", expected=("42", True))
def func_sample_04(arg1: str, *, arg2: bool):
    return arg1, arg2


@expected_args(mock.call("ARG1", action=KeyValueAction, nargs="+"),)
@call_args("foo=a", "bar=b", expected={"foo": "a", "bar": "b"})
def func_sample_05(arg1: dict):
    return arg1


@expected_args(
    mock.call("ARG1", type=str), mock.call("--arg2", action=KeyValueAction),
)
def func_sample_06(arg1: str, *, arg2: dict):
    return arg1, arg2


@expected_args(
    mock.call("ARG1", type=str), mock.call("--arg2", action="append"),
)
@call_args("foo", "--arg2", "a", "--arg2", "b", expected=("foo", ["a", "b"]))
def func_sample_07(arg1: str, *, arg2: list):
    return arg1, arg2


@expected_args(
    mock.call("ARG1", type=str), mock.call("ARG2", nargs="+"),
)
@call_args("foo", "a", "b", "c", expected=("foo", ["a", "b", "c"]))
def func_sample_08(arg1: str, arg2: list):
    return arg1, arg2


@expected_args(
    mock.call("ARG1", type=str), mock.call("--arg2", type=int, required=True),
)
@call_args("foo", "--arg2", "42", expected=("foo", 42))
def func_sample_09(arg1: str, *, arg2: int):
    return arg1, arg2


@expected_args(mock.call("ARG1", type=Colour, action=EnumName),)
@call_args("Red", expected=Colour.Red)
def func_sample_11(arg1: Colour):
    return arg1


@expected_args(
    mock.call("ARG1", type=str),
    mock.call("--arg2", type=Colour, action=EnumName, default=Colour.Red),
)
def func_sample_12(arg1: str, *, arg2: Colour = Colour.Red):
    return arg1, arg2


# FileType instances cannot be directly compared.
@expected_args(mock.call("ARG1", type=mock.ANY),)
def func_sample_13(arg1: FileType("w")):
    return arg1


@expected_args(mock.call("ARG1", type=int, nargs="+"))
@call_args("1", "2", "3", expected=[1, 2, 3])
def func_sample_14(arg1: Sequence[int]):
    return arg1


@expected_args(mock.call("--arg1", type=str, action="append"))
def func_sample_15(*, arg1: Sequence[str]):
    return arg1


@expected_args(mock.call("ARG1", type=str, action=KeyValueAction, nargs="+"))
def func_sample_16(arg1: Dict[str, str]):
    return arg1


@expected_args(mock.call("--arg1", type=str, action=KeyValueAction))
def func_sample_17(*, arg1: Dict[str, str]):
    return arg1


@expected_args(mock.call("--arg1", type=str, nargs=3))
@call_args("--arg1", "a", "b", "c", expected=["a", "b", "c"])
def func_sample_18(*, arg1: Tuple[str, str, str]):
    return arg1


@expected_args(mock.call("ARG1", type=str, nargs="?"))
@call_args(expected=None)
def func_sample_19(arg1: Optional[str]):
    return arg1


@expected_args(mock.call("--arg1", type=str, default=None))
@call_args(expected=None)
def func_sample_20(*, arg1: Optional[str]):
    return arg1


@expected_args(mock.call("ARG_1", type=int, help="foo"))
@call_args("42", expected=42)
def func_sample_21(arg_1: int = Arg(help="foo")):
    return arg_1


@expected_args(mock.call("--arg-1", "--foo", "-f", type=int, required=True))
@call_args("-f", "42", expected=42)
def func_sample_22(*, arg_1: int = Arg("--foo", "-f")):
    return arg_1


@expected_args(mock.call("--arg-1", type=int, default=42))
def func_sample_23(*, arg_1: int = Arg(default=42)):
    return arg_1


def func_sample_31(*, arg1: object() = None):
    return arg1


def func_sample_32(*, arg1: Callable[[int], None] = None):
    return arg1


def func_sample_33(*, arg1: Union[int, str, None] = None):
    return arg1


@pytest.mark.parametrize(
    "handler, expected",
    (
        (func_compatible_1, "opts"),
        (func_compatible_2, "args"),
        (func_compatible_3, "opts"),
        (func_compatible_4, "args"),
    ),
)
def test_from_parameter__compatibility(handler, expected):
    mock_parser = mock.Mock()
    proxy = CommandProxy(handler, mock_parser)

    assert proxy._require_namespace == expected
    assert mock_parser.add_argument.mock_calls == handler.expected_args


@pytest.mark.parametrize(
    "handler",
    (
        func_sample_01,
        func_sample_02,
        func_sample_03,
        func_sample_04,
        func_sample_05,
        func_sample_06,
        func_sample_07,
        func_sample_08,
        func_sample_09,
        func_sample_11,
        func_sample_12,
        func_sample_13,
        func_sample_14,
        func_sample_15,
        func_sample_16,
        func_sample_17,
        func_sample_18,
        func_sample_19,
        func_sample_20,
        func_sample_21,
        func_sample_22,
        func_sample_23,
    ),
)
def test_from_parameter__typed(handler):
    """
    Given a handler ensure expected parameters are extracted
    """
    mock_parser = mock.Mock()
    CommandProxy(handler, mock_parser)

    assert mock_parser.add_argument.mock_calls == handler.expected_args


def test_from_parameter__file_type():
    """
    Given a FileType instance ensure it is handled correctly
    """
    mock_parser = mock.Mock()
    CommandProxy(func_sample_13, mock_parser)

    actual = mock_parser.add_argument.mock_calls[0][2]["type"]
    expected = FileType("w")

    assert isinstance(actual, FileType)
    assert actual.__dict__ == expected.__dict__


def test_from_parameter__unsupported_type():
    """
    Given an unsupported type ensure correct exception is raised
    """
    mock_parser = mock.Mock()

    with pytest.raises(TypeError, match="Unsupported type"):
        CommandProxy(func_sample_31, mock_parser)


def test_from_parameter__unsupported_generic_type():
    """
    Given an unsupported generic type ensure the correct exception is raised
    """
    mock_parser = mock.Mock()

    with pytest.raises(TypeError, match="Unsupported generic type"):
        CommandProxy(func_sample_32, mock_parser)


def test_from_parameter__only_optional_unions():
    """
    Given a Union with more than 2 members ensure the correct exception is raised
    """
    mock_parser = mock.Mock()

    with pytest.raises(
        TypeError, match=r"Only Optional\[TYPE\] or Union\[TYPE, None\] are supported"
    ):
        CommandProxy(func_sample_33, mock_parser)


@pytest.mark.parametrize(
    "handler",
    (
        func_sample_02,
        func_sample_03,
        func_sample_04,
        func_sample_05,
        func_sample_07,
        func_sample_08,
        func_sample_09,
        func_sample_11,
        func_sample_14,
        func_sample_18,
        func_sample_19,
        func_sample_20,
        func_sample_21,
        func_sample_22,
    ),
)
def test_called(handler):
    """
    Given a parsed input ensure correct values are passed into the function
    """
    args, expected = handler.call_args
    parser = argparse.ArgumentParser()
    target = CommandProxy(handler, parser)
    opts = parser.parse_args(args)

    actual = target(opts)

    assert actual == expected
