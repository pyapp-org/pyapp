import pytest

from pyapp.utils import compatibility


def test_deprecated__function():
    @compatibility.deprecated("Gone in version x.y")
    def my_function():
        return "abc"

    # Assert warning not raised

    value = my_function()
    assert value == "abc"

    # Assert warning raised


def test_deprecated__class():
    @compatibility.deprecated("Gone in version x.y")
    class MyClass:
        pass

    # Assert warning not raised

    instance = MyClass()
    assert isinstance(instance, MyClass)

    # Assert warning raised
