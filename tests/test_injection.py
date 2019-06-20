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


def thing_factory(name: str = None) -> ThingBase:
    name = name or "default"
    return {"default": AThing, "b": BThing}[name]()


local_registry = injection.FactoryRegistry()
local_registry.register_factory(ThingBase, thing_factory)


def test_default_injection():
    actual = None

    @injection.inject_into(from_registry=local_registry)
    def get_value(value: ThingBase):
        nonlocal actual
        actual = value

    get_value()

    assert isinstance(actual, AThing)


def test_injection_args():
    actual = None

    @injection.inject_into(from_registry=local_registry)
    def get_value(*, value: ThingBase = injection.FactoryArgs("b")):
        nonlocal actual
        actual = value

    get_value()

    assert isinstance(actual, BThing)
