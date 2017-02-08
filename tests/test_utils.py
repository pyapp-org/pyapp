import pytest

from pyapp import utils


class IteratorTest(object):
    def __iter__(self):
        yield 1


@pytest.mark.parametrize(('instance', 'is_iterable'), (
    (None, False),
    (123, False),
    ("Foo", True),
    ([], True),
    (IteratorTest(), True),
))
def test_is_iterable(instance, is_iterable):
    assert utils.is_iterable(instance) == is_iterable


class CachedPropertyTest(object):
    def __init__(self, a, b):
        self.backing_a = a

    @utils.cached_property
    def a(self):
        return self.backing_a


def test_cached_property():
    target = CachedPropertyTest('foo', 123)

    assert target.a == 'foo'
    target.backing_a = 'bar'
    assert target.a == 'foo'
    del target.a
    assert target.a == 'bar'
