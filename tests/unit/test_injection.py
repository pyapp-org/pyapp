import abc

import pytest
from pyapp import injection


class ThingBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def do_stuff(self, item: str):
        pass


class AThing(ThingBase):
    def do_stuff(self, item: str):
        print(f"Doing A to {item}")


class BThing(ThingBase):
    def do_stuff(self, item: str):
        print(f"Doing B to {item}")


class CThing(ThingBase):
    def __init__(self):
        raise hell

    def do_stuff(self, item: str):
        pass


def thing_factory(name: str = None) -> ThingBase:
    name = name or "default"
    return {"default": AThing, "b": BThing, "c": CThing}[name]()


local_registry = injection.FactoryRegistry()
local_registry.register(ThingBase, thing_factory)


class TestFactoryRegistry:
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
    actual = None

    @injection.inject(from_registry=local_registry)
    def get_value(value: ThingBase):
        nonlocal actual
        actual = value

    get_value()

    assert isinstance(actual, AThing)


def test_inject__no_dependencies():
    actual = None

    @injection.inject(from_registry=local_registry)
    def get_value(value: str):
        nonlocal actual
        actual = value

    get_value("123")

    assert actual == "123"


def test_inject__override():
    actual = None

    @injection.inject(from_registry=local_registry)
    def get_value(*, value: ThingBase):
        nonlocal actual
        actual = value

    get_value(value=BThing())

    assert isinstance(actual, BThing)


def test_inject__with_args():
    actual = None

    @injection.inject(from_registry=local_registry)
    def get_value(*, value: ThingBase = injection.Args("b")):
        nonlocal actual
        actual = value

    get_value()

    assert isinstance(actual, BThing)


def test_inject__with_factory_args_and_not_kwarg():
    with pytest.raises(injection.InjectionSetupError):

        @injection.inject()
        def get_value(value: ThingBase = injection.Args("*")):
            pass


def test_inject__with_factory_args_and_no_type_annotation():
    with pytest.raises(injection.InjectionSetupError):

        @injection.inject()
        def get_value(*, value=injection.Args("*")):
            pass


def test_inject__factory_raises_error():
    """
    Error generated constructing a object
    """

    @injection.inject(from_registry=local_registry)
    def get_value(*, value: ThingBase = injection.Args("c")):
        pass

    with pytest.raises(injection.InjectionError):
        get_value()
