"""
Dependency Injection
~~~~~~~~~~~~~~~~~~~~

Support for dependency injection from factories.

"""

import abc
import functools
import inspect

from types import FunctionType
from typing import Callable, Dict, TypeVar, Optional

__all__ = ("FactoryRegistry", "default_registry", "register_factory", "inject")

AT_co = TypeVar("AT_co", bound=abc.ABCMeta, covariant=True)


class InjectionError(Exception):
    """
    Error that is raised if a value cannot be injected.

    This is to distinguish from a factory method raising an exception other than
    from injection.
    """


class InjectionSetupError(Exception):
    """
    Error generated during the setup of injection.
    """


class FactoryRegistry(Dict[abc.ABCMeta, Callable]):
    """
    Registry of type factories.
    """

    def register_factory(self, abstract_type: AT_co, factory: Callable):
        """
        Register a factory method for providing a abstract type.

        :param abstract_type: A type based on `abc.ABC` or using `abc.ABCMeta`
        :param factory: A factory that generates concrete instances based off the abstract type.

        """
        if not isinstance(abstract_type, abc.ABCMeta):
            raise TypeError("'abstract_type' must utilise ABCMeta")
        self[abstract_type] = factory

    def resolve_factory(self, abstract_type: AT_co) -> Optional[Callable[[], AT_co]]:
        """
        Resolve an abstract type to a factory.
        """
        return self.get(abstract_type)


# Define the global default registry
default_registry = FactoryRegistry()
register_factory = default_registry.register_factory


class FactoryArgs:
    __slots__ = ("args", "kwargs")

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def _get_factory(parameter: inspect.Parameter, registry: FactoryRegistry):
    """
    Determine if a parameter can be injected.
    """
    default = parameter.default
    if isinstance(default, FactoryArgs):
        if parameter.kind is not parameter.KEYWORD_ONLY:
            raise InjectionSetupError("Only keyword-only arguments can be injected.")

        factory = registry.resolve_factory(parameter.annotation)
        if not factory:
            raise InjectionSetupError("No type specified with factory args")

        return functools.partial(factory, *default.args, **default.kwargs)

    # Ensure that the annotation is an ABC.
    if isinstance(parameter.annotation, abc.ABCMeta):
        return registry.resolve_factory(parameter.annotation)


def _build_dependencies(func: FunctionType, registry: FactoryRegistry):
    """
    Build a list of dependency objects.
    """
    sig = inspect.signature(func)

    dependencies = []
    for name, parameter in sig.parameters.items():
        factory = _get_factory(parameter, registry)
        if factory:
            dependencies.append((name, factory))

    return tuple(dependencies)


def inject(func: FunctionType = None, *, registry: FactoryRegistry = None):
    """
    Mark a function to have arguments injected.

    A specific registry can be provided, else the global registry is used.
    """
    if func is None:
        return lambda f: inject(f, registry=registry)

    dependencies = _build_dependencies(func, registry or default_registry)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Apply dependencies
        for name, factory in dependencies:
            try:
                kwargs[name] = factory()
            except Exception as ex:
                raise InjectionError(
                    f"Unable to instantiate instance for {name}."
                ) from ex

        return func(*args, **kwargs)

    # If no dependencies are found just return original function
    return wrapper if dependencies else func
