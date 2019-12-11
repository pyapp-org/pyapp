from pyapp.utils import compatibility


def test_deprecated__function(recwarn):
    @compatibility.deprecated("Gone in version x.y")
    def my_function():
        return "abc"

    # Assert warning not raised
    assert len(recwarn) == 0

    value = my_function()
    assert value == "abc"

    # Assert warning raised
    assert len(recwarn) == 1
    assert recwarn.pop(DeprecationWarning)


def test_deprecated__class(recwarn):
    @compatibility.deprecated("Gone in version x.y")
    class MyClass:
        pass

    # Assert warning not raised
    assert len(recwarn) == 0

    instance = MyClass()
    assert isinstance(instance, MyClass)

    # Assert warning raised
    assert len(recwarn) == 1
    assert recwarn.pop(DeprecationWarning)
