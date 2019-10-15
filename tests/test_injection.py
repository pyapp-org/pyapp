import abc
import six
import pytest

from pyapp import injection


class ThingBase(six.with_metaclass(abc.ABCMeta)):
    @abc.abstractmethod
    def do_stuff(self, item):
        pass


class AThing(ThingBase):
    def do_stuff(self, item):
        print("Doing A to {}".format(item))


class BThing(ThingBase):
    def do_stuff(self, item):
        print("Doing B to {}".format(item))


class CThing(ThingBase):
    def __init__(self):
        raise hell

    def do_stuff(self, item):
        pass


def thing_factory(name=None):
    # type: (str) -> ThingBase
    name = name or "default"
    return {"default": AThing, "b": BThing, "c": CThing}[name]()


local_registry = injection.FactoryRegistry()
local_registry.register(ThingBase, thing_factory)


class TestFactoryRegistry(object):
    def test_register(self):
        target = injection.FactoryRegistry()
        target.register(ThingBase, thing_factory)

        assert len(target) == 1

    @pytest.mark.parametrize(
        "abstract_type, expected",
        ((None, None), (ThingBase, thing_factory), ("abc", None), (123, None)),
    )
    def test_resolve(self, abstract_type, expected):
        actual = local_registry.resolve(abstract_type)

        assert actual is expected


def test_inject():
    actual = {}

    @injection.inject(from_registry=local_registry)
    def get_value(value=injection.Arg(ThingBase)):
        actual[1] = value

    get_value()

    assert isinstance(actual[1], AThing)


def test_inject__no_dependencies():
    actual = {}

    @injection.inject(from_registry=local_registry)
    def get_value(foo, bar=None):
        actual[1] = foo
        actual[2] = bar

    get_value("123")

    assert actual[1] == "123"


def test_inject__override():
    actual = {}

    @injection.inject(from_registry=local_registry)
    def get_value(value=injection.Arg(ThingBase)):
        # type: (ThingBase) -> None
        actual[1] = value

    get_value(value=BThing())

    assert isinstance(actual[1], BThing)


def test_inject__with_args():
    actual = {}

    @injection.inject(from_registry=local_registry)
    def get_value(value=injection.Arg(ThingBase, "b")):
        actual[1] = value

    get_value()

    assert isinstance(actual[1], BThing)


def test_inject__with_factory_args_and_not_kwarg():
    with pytest.raises(injection.InjectionSetupError):

        @injection.inject()
        def get_value(value=injection.Arg(ThingBase, "*")):
            pass


def test_inject__with_factory_args_and_no_type_annotation():
    with pytest.raises(injection.InjectionSetupError):

        @injection.inject()
        def get_value(value=injection.Arg("*")):
            pass


def test_inject__factory_raises_error():
    """
    Error generated constructing a object
    """

    @injection.inject(from_registry=local_registry)
    def get_value(value=injection.Arg(ThingBase, "c")):
        pass

    with pytest.raises(injection.InjectionError):
        get_value()


def test_inject__invalid_args():
    """
    Error generated when non-keyword args used to override injected args
    """

    @injection.inject(from_registry=local_registry)
    def get_value(foo, bar=None, eek=injection.Arg(ThingBase)):
        # type: (str, str, ThingBase) -> None
        pass

    with pytest.raises(injection.InjectionArgumentError):
        get_value("123", "abc", AThing())
