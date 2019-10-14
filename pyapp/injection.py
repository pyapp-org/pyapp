"""
IoC (Inversion of Control) Dependency Injection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Support for automatic resolution of dependencies from factories.

These methods are built around *data annotations* and the `abc` module.

"""
from __future__ import absolute_import, print_function, unicode_literals

import abc
import functools
import inspect

from types import FunctionType
from typing import Optional, Callable, Tuple, Sequence, TypeVar, Any

__all__ = (
    "Arg",
    "FactoryRegistry",
    "default_registry",
    "register_factory",
    "inject",
    "InjectionError",
    "InjectionSetupError",
    "InjectionArgumentError",
)

AT_co = TypeVar("AT_co", bound=abc.ABCMeta, covariant=True)


class InjectionError(RuntimeError):
    """
    Exception raised if a value cannot be injected.

    These exceptions also distinguish between Exceptions raised by a factory from
    those raised by the injection framework
    """


class InjectionArgumentError(TypeError):
    """
    Invalid arguments passed to an injected method.

    This is raised if non-keyword arguments are for with injected arguments.
    """


class InjectionSetupError(Exception):
    """
    Exception generated during setup of injection.
    """


class Arg(object):
    """
    Argument used to specify an value to be injected.
    """
    __slots__ = ("type_", "args", "kwargs")

    def __init__(self, type_, *args, **kwargs):
        self.type_ = type_
        self.args = args
        self.kwargs = kwargs


class FactoryRegistry(dict):
    def register(self, abstract_type, factory):
        """
        Register a factory method that provides instances of the abstract type.

        :param abstract_type: Type the factory will produce
        :param factory: Callable that returns concrete instances of the abstract type

        """
        # type: (AT_co, Callable[..., AT_co]) -> None
        self[abstract_type] = factory

    def resolve_from_arg(self, arg):
        # type: (Arg) -> Callable[[], Any]
        factory = self.get(arg.type_)
        if not factory:
            raise InjectionSetupError("A factory for type `{}` cannot be found.".format(arg.type_))

        return functools.partial(factory, *arg.args, **arg.kwargs)


# Define global default registry
default_registry = FactoryRegistry()
register_factory = default_registry.register


def _build_dependencies(func, registry):
    # type: (FunctionType, FactoryRegistry) -> Tuple[int, Sequence[Tuple[str, Callable]]]
    """
    Build a list of dependency objects
    """
    arg_spec = inspect.getargspec(func)
    defaults = reversed(arg_spec.defaults)
    args = reversed(arg_spec.args)

    last_arg = 0
    dependencies = []
    for idx, (default, name) in enumerate(zip(defaults, args)):
        if isinstance(default, Arg):
            factory = registry.resolve_from_arg(default)
            if factory:
                last_arg = idx
                dependencies.append((name, factory))

    return len(arg_spec.args) - last_arg, dependencies


def inject(func=None, from_registry=None):
    # type: (Optional[FunctionType], Optional[FactoryRegistry]) -> Callable
    """
    Mark and function or method to have argument injected.

    A specific registry can be provided, else the global registry is used.
    """
    if func is None:
        return lambda f: inject(f, from_registry=from_registry)

    arg_count, dependencies = _build_dependencies(func, from_registry or default_registry)
    if not dependencies:
        # If no dependencies are found just return the original function
        return func

    @functools.wraps
    def wrapper(*args, **kwargs):
        if len(args) > arg_count:
            raise InjectionArgumentError("Injected args must be passed as keyword arguments.")

        for name, factory in dependencies:
            try:
                if name not in kwargs:
                    kwargs[name] = factory()
            except Exception as ex:
                raise InjectionError(
                    "Unable to instantiate argument `{}`: {!r}".format(name, ex)
                )

        return func(*args, **kwargs)

    return wrapper
