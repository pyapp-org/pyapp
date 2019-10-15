"""
IoC (Inversion of Control) Dependency Injection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Support for automatic resolution of dependencies from factories.

These methods are built around *data annotations* and the `abc` module.

Usage:

    >>> from pyapp.injection import register_factory, inject, Arg
    >>> register_factory(FooObject, foo_factory)
    # Markup methods for injection
    >>> @inject
    >>> def my_function(foo=Arg(FooObject)):
    ...     ...

When `my_function` is called `foo_factory` is used to instantiate a concrete
instance of a FooObject.

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

    def resolve(self, abstract_type):
        # type: (AT_co) -> Optional[Callable[[], AT_co]]
        """
        Resolve an abstract type to a factory.
        """
        return self.get(abstract_type)

    def resolve_from_arg(self, arg):
        # type: (Arg) -> Callable[[], AT_co]
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
    defaults = reversed(arg_spec.defaults) if arg_spec.defaults else tuple()
    args = reversed(arg_spec.args) if arg_spec.args else tuple()

    last_arg = 0
    dependencies = []
    for idx, (default, name) in enumerate(zip(defaults, args)):
        if isinstance(default, Arg):
            last_arg = idx
            factory = registry.resolve_from_arg(default)
            dependencies.append((name, factory))

    return len(arg_spec.args) - last_arg, tuple(dependencies)


def inject(func=None, from_registry=None):
    # type: (Optional[FunctionType], Optional[FactoryRegistry]) -> FunctionType
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

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) >= arg_count:
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
