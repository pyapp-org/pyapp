"""
Events
~~~~~~

A simple framework to publish events or callbacks to subscribed listener(s).

Async events/callbacks are also supported via the `AsyncEvent` and `AsyncCallback`
descriptors.

An event can have multiple listening functions whereas callbacks can only have
a single function bound (assigning a second will remove the previous binding).

.. note::

    Event and Callback descriptors do not work when ``__slots__`` are defined.
    If slots are defined a ``InstanceHasNoDictError`` will be raised on access


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
from typing import Any, Callable, Coroutine, Generic, Optional, Set, TypeVar, Union

__all__ = ("Event", "AsyncEvent", "listen_to", "Callback", "AsyncCallback", "bind_to")

_CT = TypeVar("_CT")
_F = TypeVar("_F", bound=Callable[..., Any])


class _ListenerDescriptor:
    """Common base descriptor class."""

    __slots__ = ("name",)

    set_type: type
    name: Optional[str]

    def __init__(self):
        """Initialise descriptor."""
        self.name = None

    def __set_name__(self, owner: type, name: str):
        """Assign a name to the instance."""
        if self.name is None:
            self.name = name
        elif name != self.name:
            raise TypeError(
                "Cannot assign the same event to two different names "
                f"{self.name!r} and {name!r}"
            )

    def get_listeners(self, instance):
        """Get listeners from instance."""
        if self.name is None:
            raise TypeError(
                f"Cannot use {type(self).__name__!r} instance without "
                f"calling __set_name__ on it."
            )
        try:
            return instance.__dict__[self.name]
        except AttributeError:
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to store {self.name!r} events."
            )
            raise TypeError(msg) from None
        except KeyError:
            return None

    def set_listeners(self, instance, listeners):
        """Store listeners on instance."""
        # Called by subclasses, all access checks are performed in the get method
        instance.__dict__[self.name] = listeners
        return listeners


class ListenerContext(Generic[_CT]):
    """Context manager to manage temporary listeners.

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
class BaseListenerSet(Set[_CT]):
    """Set of event listeners."""

    __slots__ = ()

    def __repr__(self):
        listeners = sorted(c.__qualname__ for c in self)
        return f"ListenerSet({', '.join(listeners)})"

    def __iadd__(self, other: Union[Set[_CT], _CT]) -> "BaseListenerSet[_CT]":
        """Allow listeners to be registered using the += operator."""
        # Merge sets
        if isinstance(other, set):
            self.update(other)
        else:
            self.add(other)
        return self

    def tap(self, listener: _CT) -> ListenerContext[_CT]:
        """Tap into an event with a temporary context.

        :param listener: Listener callback method
        :return: Context manager

        Example::

            with instance.my_event.tap(callback):
                pass

        """
        return ListenerContext[_CT](listener, self)


class ListenerSet(BaseListenerSet[_CT]):
    """Set of event listeners."""

    __slots__ = ()

    def __call__(self, *args, **kwargs):
        """
        Trigger event and call listeners.
        """
        for callback in self:
            callback(*args, **kwargs)


class Event(Generic[_CT], _ListenerDescriptor):
    """Event publisher descriptor.

    Used to gain access to the listener list.

    """

    __slots__ = ()

    def __get__(self, instance, owner) -> ListenerSet[_CT]:
        if listeners := self.get_listeners(instance):
            return listeners
        return self.set_listeners(instance, ListenerSet())


_ACT = TypeVar("_ACT", bound=Union[Callable[..., Coroutine], "AsyncListenerSet"])


class AsyncListenerSet(BaseListenerSet[_ACT]):
    """Set of event listeners."""

    __slots__ = ()

    async def __call__(self, *args, **kwargs):
        """
        Trigger event and call listeners.
        """
        awaitables = [asyncio.create_task(c(*args, **kwargs)) for c in self]
        if awaitables:
            await asyncio.wait(awaitables, return_when=asyncio.ALL_COMPLETED)


class AsyncEvent(Generic[_ACT], _ListenerDescriptor):
    """Async event publisher descriptor.

    Used to gain access to the listener list.

    """

    __slots__ = ()

    def __get__(self, instance, owner) -> ListenerSet[_ACT]:
        if listeners := self.get_listeners(instance):
            return listeners
        return self.set_listeners(instance, AsyncListenerSet())


def listen_to(event: ListenerSet[_F]) -> Callable[[_F], _F]:
    """Decorator for attaching listeners to events."""

    def decorator(func: _F) -> _F:
        event.add(func)
        return func

    return decorator


class CallbackBindingBase(Generic[_CT]):
    """Descriptor binding instance that provides a single method binding."""

    __slots__ = ("_callback",)

    def __init__(self):
        self._callback: Optional[_CT] = None

    def __iadd__(self, callback: _CT) -> "CallbackBindingBase[_CT]":
        self._callback = callback
        return self

    def bind(self, callback: _CT):
        """Bind callback."""
        self._callback = callback

    def unbind(self):
        """Unbind the callback."""
        self._callback = None


class CallbackBinding(CallbackBindingBase[_ACT]):
    """Descriptor binding instance that provides a single method binding."""

    __slots__ = ()

    def __call__(self, *args, **kwargs):
        if self._callback:
            return self._callback(*args, **kwargs)
        return None


class Callback(Generic[_CT], _ListenerDescriptor):
    """Callback descriptor.

    Used to attach a single callback.

    """

    __slots__ = ()

    def __get__(self, instance, owner) -> CallbackBinding[_CT]:
        if listeners := self.get_listeners(instance):
            return listeners
        return self.set_listeners(instance, CallbackBinding())


class AsyncCallbackBinding(CallbackBindingBase[_ACT]):
    """Descriptor binding instance that provides a single method binding."""

    __slots__ = ()

    async def __call__(self, *args, **kwargs):
        if self._callback:
            return await self._callback(*args, **kwargs)


class AsyncCallback(Generic[_ACT], _ListenerDescriptor):
    """Async callback descriptor.

    Use to attach a single async callback

    """

    __slots__ = ()

    def __get__(self, instance, owner) -> AsyncCallbackBinding[_ACT]:
        if listeners := self.get_listeners(instance):
            return listeners
        return self.set_listeners(instance, AsyncCallbackBinding())


def bind_to(callback: CallbackBinding[_F]) -> Callable[[_F], _F]:
    """Decorator for attaching a listener to a callback."""

    def decorator(func: _F) -> _F:
        callback.bind(func)
        return func

    return decorator
