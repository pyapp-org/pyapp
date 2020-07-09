import pytest

from unittest import mock
from typing import Sequence

from pyapp.app.arguments import Arg, CommandProxy


def func_backwards_compatible_1(opts):
    pass


def func_backwards_compatible_2(opts):
    pass


def func_sample_1():
    pass


def func_sample_2(arg1: str):
    pass


def func_sample_3(arg1: Sequence[str]):
    pass


def func_sample_4(arg1: int = Arg(name="foo")):
    pass


def func_sample_5(arg1: str, *, arg2: str = "foo"):
    pass


def func_sample_6(arg1: str, *, arg2: bool):
    pass


def func_sample_7(arg1: str, *, arg2: dict):
    pass


def func_sample_8(arg1: str, *, arg2: dict):
    pass


@pytest.mark.parametrize(
    "handler, expected",
    (
        # (func_backwards_compatible_1, {}),
        # (func_backwards_compatible_2, {}),
        # (func_sample_1, {}),
        (func_sample_2, [(("arg1",), {})]),
        (func_sample_3, [(("arg1",), {})]),
        (func_sample_4, [(("arg1",), {})]),
        (func_sample_5, [(("arg1",), {})]),
        (func_sample_6, [(("arg1",), {})]),
        (func_sample_7, [(("arg1",), {})]),
        (func_sample_8, [(("arg1",), {})]),
    ),
)
def test_from_parameter(handler, expected):
    mock_parser = mock.Mock()
    CommandProxy(handler, mock_parser)

    mock_parser.add_argument.assert_called()
