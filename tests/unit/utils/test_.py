import pytest
from pyapp import utils


class IteratorTest:
    def __iter__(self):
        yield 1


@pytest.mark.parametrize(
    ("instance", "is_iterable"),
    ((None, False), (123, False), ("Foo", True), ([], True), (IteratorTest(), True)),
)
def test_is_iterable(instance, is_iterable):
    assert utils.is_iterable(instance) == is_iterable


class CachedPropertyTest:
    def __init__(self, a, b):
        self.backing_a = a

    @utils.cached_property
    def a(self):
        return self.backing_a


def test_cached_property():
    target = CachedPropertyTest("foo", 123)

    assert target.a == "foo"
    target.backing_a = "bar"
    assert target.a == "foo"
    del target.a
    assert target.a == "bar"


@pytest.mark.parametrize(
    "value, expected",
    (
        ("yes", True),
        ("True", True),
        ("y", True),
        ("t", True),
        ("ON", True),
        ("1", True),
        ("", False),
        ("FALSE", False),
        ("Off", False),
        (None, False),
    ),
)
def test_text_to_bool(value, expected):
    actual = utils.text_to_bool(value)

    assert actual == expected


class TestAllowBlockFilter:
    @pytest.mark.parametrize(
        "allow_list, block_list, value, expected",
        (
            # Allow all
            (None, None, "foo", True),
            # Allow/Block specific
            (["foo"], None, "foo", True),
            (["foo"], None, "bar", False),
            (None, ["foo"], "foo", False),
            (None, ["foo"], "bar", True),
            # Allow/Block glob
            (["foo*"], None, "foo", True),
            (["foo*"], None, "foobar", True),
            (["foo*"], None, "bar", False),
            (None, ["foo*"], "foo", False),
            (None, ["foo*"], "foobar", False),
            (None, ["foo*"], "bar", True),
            # Combined
            (["foo*"], ["bar*"], "foo", True),
            (["foo*"], ["bar*"], "foobar", True),
            (["foo*"], ["bar*"], "bar", False),
            (["foo*"], ["bar*"], "barfoo", False),
            (["foo*"], ["bar*"], "eek", False),
        ),
    )
    def test_filtering(self, allow_list, block_list, value, expected):
        target = utils.AllowBlockFilter(allow_list=allow_list, block_list=block_list)

        assert target(value) is expected
