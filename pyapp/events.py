"""
Events
~~~~~~

A simple framework publish events from a class that can be subscribed to.

Async events are also supported via the `AsyncEvent` descriptor.

Example::

    class MyClass:

        started = Event[Callable[[], None]]()
        new_message = AsyncEvent[Callable[[str], Awaitable]]()

        def start(self):
            self.started.trigger()

        async def process_message(self, message):
            await self.new_message.trigger(message)


    instance = MyClass()

    @instance.started
    def on_started():
        pass

    async def on_new_message(message: str):
        pass

    instance.new_message += on_new_message


"""
import asyncio

from typing import Callable, Union, Generic, TypeVar, List, Coroutine, Iterable

__all__ = ("Event", "AsyncEvent")

_CT = TypeVar("_CT")


class ListenerList(List[_CT]):
    """
    List of event listeners.
    """

    __slots__ = tuple()

    def __repr__(self):
        names = (
            c.__func__.__qualname__ if hasattr(c, "__func__") else repr(c) for c in self
        )
        return f"[{', '.join(names)}]"

    def __iadd__(self, other: Union["ListenerList[_CT]", _CT]) -> "ListenerList[_CT]":
        """
        Allow listeners to be registered using the += operator.
        """
        self.append(other)
        return self

    def trigger(self, *args, **kwargs):
        """
        Trigger event and call listeners.
        """
        for callback in self:
            callback(*args, **kwargs)


class Event(Generic[_CT]):
    """
    Event publisher descriptor.

    Used to gain access to the listener list.

    """

    __slots__ = tuple()

    def __get__(self, instance, owner) -> ListenerList[_CT]:
        return ListenerList()


_ACT = TypeVar("_ACT", bound=Union[Callable[..., Coroutine], "AsyncListenerList"])


class AsyncListenerList(ListenerList[_ACT]):
    """
    List of event listeners.
    """

    __slots__ = tuple()

    def __repr__(self):
        names = (
            c.__func__.__qualname__ if hasattr(c, "__func__") else repr(c) for c in self
        )
        return f"[{', '.join(names)}]"

    def append(self, other: Union["AsyncListenerList[_ACT]", _ACT]):
        # Unpack listener list so they can be awaited together.
        if isinstance(other, Iterable):
            super().extend(other)
        else:
            super().append(other)

    async def trigger(self, *args, **kwargs):
        """
        Trigger event and call listeners.
        """
        # Events are all triggered and all awaited at once.
        await asyncio.wait([c(*args, **kwargs) for c in self])


class AsyncEvent(Generic[_ACT]):
    """
    Async event publisher descriptor.

    Used to gain access to the listener list.

    """

    __slots__ = tuple()

    def __get__(self, instance, owner) -> AsyncListenerList[_ACT]:
        return AsyncListenerList()


def listen_to(event: ListenerList):
    def decorator(func):
        event += decorator
        return funct
