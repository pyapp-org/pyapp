"""
Conf Helper Bases
~~~~~~~~~~~~~~~~~

"""
import abc
import threading
from abc import ABCMeta
from typing import Any
from typing import Generic
from typing import TypeVar


class DefaultCache(dict):
    """
    Very similar to :py:class:`collections.defaultdict` (using __missing__)
    however passes the specified key to the default factory method.
    """

    __slots__ = ("default_factory",)

    def __init__(self, default_factory=None, **kwargs):
        super().__init__(**kwargs)
        self.default_factory = default_factory

    def __missing__(self, key: Any):
        if not self.default_factory:
            raise KeyError(key)
        self[key] = value = self.default_factory(key)
        return value


FT = TypeVar("FT")


class FactoryMixin(Generic[FT], metaclass=ABCMeta):
    """
    Mixing to provide a factory interface
    """

    __slots__ = ()

    @abc.abstractmethod
    def create(self, name: str = None) -> FT:
        """
        Create an instance based on a named setting.
        """


class SingletonFactoryMixin(FactoryMixin[FT], metaclass=ABCMeta):
    """"
    Mixin that provides a single named instance.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents.

    If your instance types are not thread safe it is recommended that the
    :py:class:`ThreadLocalSingletonFactoryMixin` is used.

    """

    __slots__ = ("_instances",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._instances = DefaultCache(self.create)
        instances_lock = threading.RLock()

        def create_wrapper(name: str = None) -> FT:
            with instances_lock:
                return self._instances[name]

        self.create = create_wrapper


class ThreadLocalSingletonFactoryMixin(FactoryMixin[FT], metaclass=ABCMeta):
    """
    Mixin that provides a single named instance per thread.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents and that are
    not thread safe.

    """

    __slots__ = ("_instances",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._instances = threading.local()
        create = self.create

        def create_wrapper(name: str = None) -> FT:
            try:
                cache = self._instances.cache
            except AttributeError:
                cache = self._instances.cache = DefaultCache(create)
            return cache[name]

        self.create = create_wrapper
