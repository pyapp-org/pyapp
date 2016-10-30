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
