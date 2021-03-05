"""
IoC (Inversion of Control) Dependency Injection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Support for automatic resolution of dependencies from factories.

These methods are built around *data annotations* and `abc` module.

Usage::

    # Register factory with framework
    >>> pyapp.injection.register_factory(FooABC, foo_factory)

    # Mark functions for injection and specify type
    >>> @inject
    ... def my_function(foo: FooABC = Args(name="second")):
    ...    ...

What `my_function` is called a concrete instance that implements `FooABC` is
passed into the function.

"""
import abc
import functools
import inspect
from types import FunctionType
from typing import Callable
from typing import Dict
from typing import Optional
from typing import TypeVar

__all__ = (
    "Args",
    "FactoryRegistry",
    "default_registry",
    "register_factory",
    "inject",
    "InjectionError",
    "InjectionSetupError",
)

# pylint: disable=invalid-name
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


# TODO: Remove when pylint handles typing.Dict correctly  pylint: disable=fixme
# pylint: disable=unsupported-assignment-operation,no-member
class FactoryRegistry(Dict[type, Callable]):
    """
    Registry of type factories.
    """

    def register(self, abstract_type: AT_co, factory: Callable[..., AT_co]):
        """
        Register a factory method for providing a abstract type.

        :param abstract_type: Type factory will produce
        :param factory: A factory that generates concrete instances based off the abstract type.

        """
        self[abstract_type] = factory

    def resolve(self, abstract_type: AT_co) -> Optional[Callable[[], AT_co]]:
        """
        Resolve an abstract type to a factory.
        """
        return self.get(abstract_type)

    def resolve_from_parameter(
        self, parameter: inspect.Parameter
    ) -> Callable[[], AT_co]:
        """
        Resolve an abstract type from an `Parameter`.
        """
        default = parameter.default
        if isinstance(default, Args):
            if parameter.kind is not parameter.KEYWORD_ONLY:
                raise InjectionSetupError(
                    "Only keyword-only arguments can be injected."
                )

            factory = self.get(parameter.annotation)
            if not factory:
                raise InjectionSetupError("A type must be specified with `FactoryArgs`")

            return functools.partial(factory, *default.args, **default.kwargs)

        # Ensure that the annotation is an ABC.
        return self.get(parameter.annotation)


# Define the global default registry
default_registry = FactoryRegistry()
register_factory = default_registry.register


class Args:
    """
    Arguments to provide to factory.

    These are commonly used for named config factories where a particular
    configuration is expected. A good example might be the name of a message
    queue.

    """

    __slots__ = ("args", "kwargs")

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


# Fallback
FactoryArgs = Args


def _build_dependencies(func: FunctionType, registry: FactoryRegistry):
    """
    Build a list of dependency objects.
    """
    sig = inspect.signature(func)

    dependencies = []
    for name, parameter in sig.parameters.items():
        factory = registry.resolve_from_parameter(parameter)
        if factory:
            dependencies.append((name, factory))

    return tuple(dependencies)


def inject(func: FunctionType = None, *, from_registry: FactoryRegistry = None):
    """
    Mark a function to have arguments injected.

    A specific registry can be provided, else the global registry is used.
    """
    if func is None:
        return lambda f: inject(f, from_registry=from_registry)

    dependencies = _build_dependencies(func, from_registry or default_registry)
    if not dependencies:
        # If no dependencies are found just return original function
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Apply dependencies
        for name, factory in dependencies:
            try:
                if name not in kwargs:
                    kwargs[name] = factory()
            except Exception as ex:
                raise InjectionError(
                    f"Unable to instantiate argument `{name}`: {ex!r}"
                ) from ex

        return func(*args, **kwargs)

    return wrapper
