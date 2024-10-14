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
from collections.abc import Callable
from types import FunctionType
from typing import Any, Protocol, TypeVar

from typing_extensions import Self

__all__ = (
    "Args",
    "FactoryRegistry",
    "default_registry",
    "register_factory",
    "inject",
    "InjectionError",
    "InjectionSetupError",
    "ModifyFactoryRegistryContext",
)

AT_co = TypeVar("AT_co", bound=abc.ABC, covariant=True)


class FactoryFunc(Protocol[AT_co]):
    def __call__(self, *args, **kwargs) -> AT_co:
        ...


class InjectionError(Exception):
    """Error that is raised if a value cannot be injected.

    This is to distinguish from a factory method raising an exception other than
    from injection.
    """


class InjectionSetupError(Exception):
    """Error generated during the setup of injection."""


class ModifyFactoryRegistryContext:
    """Context object used to make temporary modifications to factory registry.

    The main use-case for this feature is within test cases.

    Mocks can be changed and when the context is exited the changes are reverted.
    """

    __slots__ = ("__registry", "__rollback")

    def __init__(self, registry: "FactoryRegistry"):
        self.__registry = registry
        self.__rollback = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore the state by running the rollback actions in reverse
        for action, args in reversed(self.__rollback):
            action(*args)

    def __setitem__(self, abstract_type: type[AT_co], factory: FactoryFunc[AT_co]):
        """Replace a factory for an abstract type."""

        assert issubclass(abstract_type, abc.ABC), "Expected an `abstract type` key"  # noqa: S101 - Assertions used in testing
        assert callable(factory), "Expected a `callable` value"  # noqa: S101 - Assertions used in testing

        if abstract_type in self.__registry:
            # Prepare an action that puts the current value back
            action = (
                self.__registry.__setitem__,
                (abstract_type, self.__registry[abstract_type]),
            )
        else:
            # Prepare an action to remove the type
            action = self.__registry.__delitem__, (abstract_type,)
        self.__rollback.append(action)

        self.__registry[abstract_type] = factory

    def mock_type(self, abstract_type: type[AT_co], *, allow_missing: bool = False):
        """Replace a factory with one that will always return a mock type.

        This method will raise an assertion if the abstract type is not found
        in the registry. The assertion can be disabled by setting ``allow_missing``
        to ``True``.

        Will return the generated mock.
        """
        from unittest.mock import Mock

        assert issubclass(abstract_type, abc.ABC), "Expected an abstract type"  # noqa: S101 - Assertions used in testing

        if not allow_missing:
            assert (  # noqa: S101 - Assertions used in testing
                abstract_type in self.__registry
            ), f"{abstract_type} not found in registry"

        mock = Mock(spec=abstract_type)
        self[abstract_type] = lambda *args, **kwargs: mock
        return mock


class FactoryRegistry(dict[type[AT_co], Callable]):
    """Registry of type factories."""

    def register(self, abstract_type: type[AT_co], factory: FactoryFunc):
        """Register a factory method for providing an abstract type.

        :param abstract_type: Type factory will produce
        :param factory: A factory that generates concrete instances based off the abstract type.

        """

        self[abstract_type] = factory

    def resolve(self, abstract_type: type[AT_co]) -> FactoryFunc | None:
        """Resolve an abstract type to a factory."""

        return self.get(abstract_type)

    def resolve_from_parameter(
        self, parameter: inspect.Parameter
    ) -> Callable[[], AT_co]:
        """Resolve an abstract type from an `Parameter`."""

        default = parameter.default
        if isinstance(default, Args):
            if parameter.kind is not parameter.KEYWORD_ONLY:
                raise InjectionSetupError(
                    "Only keyword-only arguments can be injected."
                )

            factory = self.get(parameter.annotation)
            if not factory:
                raise InjectionSetupError("A type must be specified with `Args`")

            return functools.partial(factory, *default.args, **default.kwargs)

        # Ensure that the annotation is an ABC.
        return self.get(parameter.annotation)

    def modify(self) -> ModifyFactoryRegistryContext:
        """
        Apply changes to factory registry using a context manager that will roll back
        the changes on exit of a with block. Designed to simplify test cases.

        This should be used with a context manager:

            >>> with default_registry.modify() as patch:
            >>>     class MyType(abc.ABC):
            >>>         pass
            >>>     # Replace with a mock
            >>>     mock = patch.mock_type(MyType)
            >>>     # Replace with a custom factory
            >>>     patch[MyType] = lambda : MyType()

        """
        return ModifyFactoryRegistryContext(self)


# Define the global default registry
default_registry = FactoryRegistry()
register_factory = default_registry.register


class Args:
    """Arguments to provide to factory.

    These are commonly used for named config factories where a particular
    configuration is expected. A good example might be the name of a message
    queue.

    """

    __slots__ = ("args", "kwargs")

    def __init__(self, *args, **kwargs):
        """Initialise Arguments."""

        self.args = args
        self.kwargs = kwargs


# Fallback
FactoryArgs = Args


def _build_dependencies(func: FunctionType, registry: FactoryRegistry):
    """Build a list of dependency objects."""
    sig = inspect.signature(func)

    dependencies = []
    for name, parameter in sig.parameters.items():
        factory = registry.resolve_from_parameter(parameter)
        if factory:
            dependencies.append((name, factory))

    return tuple(dependencies)


_F = TypeVar("_F", bound=Callable[..., Any])


def inject(
    func: _F = None,
    *,
    from_registry: FactoryRegistry = None,
) -> _F | Callable[[_F], _F]:
    """Mark a function to have arguments injected.

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
