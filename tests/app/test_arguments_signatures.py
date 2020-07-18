from argparse import FileType
from enum import Enum
from typing import Callable
from typing import Dict
from typing import Sequence
from typing import Tuple
from unittest import mock

import pytest

from pyapp.app import CommandOptions
from pyapp.app.argument_actions import EnumName
from pyapp.app.argument_actions import KeyValueAction
from pyapp.app.arguments import Arg
from pyapp.app.arguments import CommandProxy


def expected_args(*args):
    """
    Helper for applying expected add_argment calls to test functions
    """

    def _wrapper(func):
        func.expected = list(args)
        return func

    return _wrapper


class Colour(Enum):
    Red = "red"
    Green = "green"


@expected_args()
def func_compatible_1(opts):
    pass


@expected_args()
def func_compatible_2(args: CommandOptions):
    pass


@expected_args(mock.call("--arg-1", type=int, dest="arg_1", default=42))
def func_compatible_3(opts: CommandOptions, *, arg_1: int = Arg(default=42)):
    pass


@expected_args(mock.call("--arg-1", type=int, dest="arg_1", default=42))
def func_compatible_4(*, arg_1: int = Arg(default=42), args: CommandOptions):
    pass


@expected_args()
def func_sample_01():
    pass


@expected_args(mock.call("arg1", type=int, dest="arg1"))
def func_sample_02(arg1: int):
    pass


@expected_args(
    mock.call("arg1", type=str, dest="arg1"),
    mock.call("--arg2", type=str, dest="arg2", default="foo"),
)
def func_sample_03(arg1: str, *, arg2: str = "foo"):
    pass


@expected_args(
    mock.call("arg1", type=str, dest="arg1"),
    mock.call("--arg2", action="store_true", dest="arg2"),
)
def func_sample_04(arg1: str, *, arg2: bool):
    pass


@expected_args(mock.call("arg1", action=KeyValueAction, dest="arg1", nargs="+"),)
def func_sample_05(arg1: dict):
    pass


@expected_args(
    mock.call("arg1", type=str, dest="arg1"),
    mock.call("--arg2", action=KeyValueAction, dest="arg2"),
)
def func_sample_06(arg1: str, *, arg2: dict):
    pass


@expected_args(
    mock.call("arg1", type=str, dest="arg1"),
    mock.call("--arg2", dest="arg2", action="append"),
)
def func_sample_07(arg1: str, *, arg2: list):
    pass


@expected_args(
    mock.call("arg1", type=str, dest="arg1"),
    mock.call("arg2", dest="arg2", action="append", nargs="+"),
)
def func_sample_08(arg1: str, arg2: list):
    pass


@expected_args(
    mock.call("arg1", type=str, dest="arg1"),
    mock.call("--arg2", type=int, dest="arg2", required=True),
)
def func_sample_09(arg1: str, *, arg2: int):
    pass


@expected_args(
    mock.call("arg1", type=str, dest="arg1"),
    mock.call("--arg2", type=Colour, action=EnumName, dest="arg2", default=Colour.Red),
)
def func_sample_11(arg1: str, *, arg2: Colour = Colour.Red):
    pass


# FileType instances cannot be directly compared.
@expected_args(mock.call("arg1", type=mock.ANY, dest="arg1"),)
def func_sample_12(arg1: FileType("w")):
    pass


@expected_args(mock.call("arg1", type=str, dest="arg1", action="append", nargs="+"))
def func_sample_13(arg1: Sequence[str]):
    pass


@expected_args(mock.call("--arg1", type=str, dest="arg1", action="append"))
def func_sample_14(*, arg1: Sequence[str]):
    pass


@expected_args(
    mock.call("arg1", type=str, action=KeyValueAction, dest="arg1", nargs="+")
)
def func_sample_15(arg1: Dict[str, str]):
    pass


@expected_args(mock.call("--arg1", type=str, action=KeyValueAction, dest="arg1"))
def func_sample_16(*, arg1: Dict[str, str]):
    pass


@expected_args(mock.call("--arg1", type=str, dest="arg1", nargs=3))
def func_sample_17(*, arg1: Tuple[str, str, str]):
    pass


@expected_args(
    mock.call("--arg-1", "--foo", "-f", type=int, dest="arg_1", required=True)
)
def func_sample_21(*, arg_1: int = Arg("--foo", "-f")):
    pass


@expected_args(mock.call("--arg-1", type=int, dest="arg_1", default=42))
def func_sample_22(*, arg_1: int = Arg(default=42)):
    pass


def func_sample_31(*, arg1: object() = None):
    pass


def func_sample_32(*, arg1: Callable[[int], None] = None):
    pass


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
    assert mock_parser.add_argument.mock_calls == handler.expected


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
        func_sample_21,
        func_sample_22,
    ),
)
def test_from_parameter__typed(handler):
    mock_parser = mock.Mock()
    CommandProxy(handler, mock_parser)

    assert mock_parser.add_argument.mock_calls == handler.expected


def test_from_parameter__file_type():
    mock_parser = mock.Mock()
    CommandProxy(func_sample_12, mock_parser)

    actual = mock_parser.add_argument.mock_calls[0][2]["type"]
    expected = FileType("w")

    assert isinstance(actual, FileType)
    assert actual.__dict__ == expected.__dict__


def test_from_parameter__unsupported_type():
    mock_parser = mock.Mock()

    with pytest.raises(TypeError, match="Unsupported type"):
        CommandProxy(func_sample_31, mock_parser)


def test_from_parameter__unsupported_generic_type():
    mock_parser = mock.Mock()

    with pytest.raises(TypeError, match="Unsupported generic type"):
        CommandProxy(func_sample_32, mock_parser)
