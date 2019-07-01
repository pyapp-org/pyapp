"""
Events
~~~~~~

A simple framework publish events from a class to subscribed listeners.

Async events are also supported via the `AsyncEvent` descriptor.

Example::

    class MyClass:
        started = Event[Callable[[], None]]()
        new_message = AsyncEvent[Callable[[str], Awaitable]]()

        def start(self):
            self.started()

        async def process_message(self, message):
            await self.new_message(message)


    instance = MyClass()

    @listen_to(instance.started)
    def on_started():
        pass

    async def on_new_message(message: str):
        pass

    instance.new_message += on_new_message


.. hint::

    Listener lists (providing their event signatures match) can be appended to another
    event.

"""
import asyncio

from typing import Callable, Union, Generic, TypeVar, Set, Coroutine

__all__ = ("Event", "AsyncEvent", "listen_to")


_CT = TypeVar("_CT")


class ListenerContext(Generic[_CT]):
    """
    Context manager to manage temporary listeners.

    This is useful for testing.
    """

    __slots__ = ("listener", "listeners")

    def __init__(self, listener: _CT, listeners: Set[_CT]):
        self.listener = listener
        self.listeners = listeners

    def __enter__(self) -> None:
        self.listeners.add(self.listener)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.listeners.remove(self.listener)


class ListenerSet(Set[_CT]):
    """
    Set of event listeners.
    """

    __slots__ = tuple()

    def __repr__(self):
        listeners = sorted(c.__qualname__ for c in self)
        return f"ListenerSet({', '.join(listeners)})"

    def __iadd__(self, other: Union[Set[_CT], _CT]) -> "ListenerSet[_CT]":
        """
        Allow listeners to be registered using the += operator.
        """
        # Merge sets
        if isinstance(other, set):
            self.update(other)
        else:
            self.add(other)
        return self

    def __call__(self, *args, **kwargs):
        """
        Trigger event and call listeners.
        """
        for callback in self:
            callback(*args, **kwargs)

    def tap(self, listener: _CT) -> ListenerContext[_CT]:
        """
        Tap into an event with a temporary context.

        :param listener: Listener callback method
        :return: Context manager

        Example::

            with instance.my_event.tap(callback):
                pass

        """
        return ListenerContext[_CT](listener, self)


class Event(Generic[_CT]):
    """
    Event publisher descriptor.

    Used to gain access to the listener list.

    """

    __slots__ = ("_instances",)

    def __init__(self):
        self._instances = {}

    def __get__(self, instance, owner) -> ListenerSet[_CT]:
        try:
            return self._instances[id(instance)]
        except KeyError:
            self._instances[id(instance)] = listeners = ListenerSet()
            return listeners


_ACT = TypeVar("_ACT", bound=Union[Callable[..., Coroutine], "AsyncListenerList"])


class AsyncListenerSet(ListenerSet[_ACT]):
    """
    List of event listeners.
    """

    __slots__ = tuple()

    async def __call__(self, *args, **kwargs):
        """
        Trigger event and call listeners.
        """
        aw = [c(*args, **kwargs) for c in self]
        if aw:
            await asyncio.wait(aw)


class AsyncEvent(Generic[_ACT]):
    """
    Async event publisher descriptor.

    Used to gain access to the listener list.

    """

    __slots__ = ("_instances",)

    def __init__(self):
        self._instances = {}

    def __get__(self, instance, owner) -> ListenerSet[_ACT]:
        try:
            return self._instances[id(instance)]
        except KeyError:
            self._instances[id(instance)] = listeners = AsyncListenerSet()
            return listeners


def listen_to(event: ListenerSet[_CT]) -> _CT:
    """
    Decorator for attaching listeners to events
    """

    def decorator(func: _CT) -> _CT:
        event.add(func)
        return func

    return decorator
