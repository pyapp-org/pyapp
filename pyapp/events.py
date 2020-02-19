"""
Events
~~~~~~

A simple framework publish events or callbacks from a class to subscribed listener(s).

Async events/callbacks are also supported via the `AsyncEvent` and `AsyncCallback`
descriptors.

Event can have multiple listening functions where callbacks can only have a single
function bound (assigning a second will remove the previous).

Example::

    class MyClass:
        started = Event[Callable[[], None]]()
        new_message = AsyncCallback[Callable[[str], Awaitable]]()

        def start(self):
            self.started()

        async def process_message(self, message):
            await self.handle_message(message)


    instance = MyClass()

    @listen_to(instance.started)
    def on_started():
        pass

    @bind_to(instance.new_message)
    async def on_new_message(message: str):
        pass


.. hint::

    Listener lists (providing their event signatures match) can be appended to another
    event.

"""
import asyncio
from typing import Callable
from typing import Coroutine
from typing import Generic
from typing import Optional
from typing import Set
from typing import TypeVar
from typing import Union

__all__ = ("Event", "AsyncEvent", "listen_to", "Callback", "AsyncCallback", "bind_to")


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


# TODO: Remove when pylint handles typing.Set correctly  pylint: disable=fixme
# pylint: disable=not-an-iterable,no-member
class ListenerSet(Set[_CT]):
    """
    Set of event listeners.
    """

    __slots__ = ()

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

    __slots__ = ("name",)

    def __get__(self, instance, owner) -> ListenerSet[_CT]:
        try:
            return instance.__dict__[self.name]
        except KeyError:
            instance.__dict__[self.name] = listeners = ListenerSet()
            return listeners

    def __set_name__(self, owner, name):
        self.name = name  # pylint: disable=attribute-defined-outside-init


_ACT = TypeVar("_ACT", bound=Union[Callable[..., Coroutine], "AsyncListenerList"])


class AsyncListenerSet(ListenerSet[_ACT]):
    """
    List of event listeners.
    """

    __slots__ = ()

    async def __call__(self, *args, **kwargs):
        """
        Trigger event and call listeners.
        """
        awaitables = [c(*args, **kwargs) for c in self]
        if awaitables:
            await asyncio.wait(awaitables, return_when=asyncio.ALL_COMPLETED)


class AsyncEvent(Generic[_ACT]):
    """
    Async event publisher descriptor.

    Used to gain access to the listener list.

    """

    __slots__ = ("name",)

    def __get__(self, instance, owner) -> ListenerSet[_ACT]:
        try:
            return instance.__dict__[self.name]
        except KeyError:
            instance.__dict__[self.name] = listeners = AsyncListenerSet()
            return listeners

    def __set_name__(self, owner, name):
        self.name = name  # pylint: disable=attribute-defined-outside-init


def listen_to(event: ListenerSet[_CT]) -> _CT:
    """
    Decorator for attaching listeners to events
    """

    def decorator(func: _CT) -> _CT:
        event.add(func)
        return func

    return decorator


class CallbackBinding(Generic[_CT]):
    """
    Descriptor binding instance that provides a single method binding.
    """

    __slots__ = ("_callback",)

    def __init__(self):
        self._callback: Optional[_CT] = None

    def __iadd__(self, callback: _CT) -> "CallbackBinding[_CT]":
        self._callback = callback
        return self

    def bind(self, callback: _CT):
        """
        Bind callback
        """
        self._callback = callback

    def unbind(self):
        """
        Unbind the callback
        """
        self._callback = None

    def __call__(self, *args, **kwargs):
        if self._callback:
            self._callback(*args, **kwargs)


class Callback(Generic[_CT]):
    """
    Callback descriptor.

    Used to attach a single callback.

    """

    __slots__ = ("name",)

    def __get__(self, instance, owner) -> CallbackBinding[_CT]:
        try:
            return instance.__dict__[self.name]
        except KeyError:
            instance.__dict__[self.name] = wrapper = CallbackBinding[_CT]()
            return wrapper

    def __set_name__(self, owner, name):
        self.name = name  # pylint: disable=attribute-defined-outside-init


class AsyncCallbackBinding(CallbackBinding[_ACT]):
    """
    Descriptor binding instance that provides a single method binding.
    """

    __slots__ = ()

    async def __call__(self, *args, **kwargs):
        if self._callback:
            return await self._callback(*args, **kwargs)


class AsyncCallback(Generic[_ACT]):
    """
    Async callback descriptor

    Use to attach a single async callback

    """

    __slots__ = ("name",)

    def __get__(self, instance, owner) -> AsyncCallbackBinding[_ACT]:
        try:
            return instance.__dict__[self.name]
        except KeyError:
            instance.__dict__[self.name] = wrapper = AsyncCallbackBinding[_ACT]()
            return wrapper

    def __set_name__(self, owner, name):
        self.name = name  # pylint: disable=attribute-defined-outside-init


def bind_to(callback: CallbackBinding[_CT]) -> _CT:
    """
    Decorator for attaching a listener to a callback
    """

    def decorator(func: _CT) -> _CT:
        callback.bind(func)
        return func

    return decorator
