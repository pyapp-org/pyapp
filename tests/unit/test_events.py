from typing import Awaitable, Callable

import pytest
from pyapp import events


class TestListenerSet:
    @pytest.fixture
    def target(self):
        def on_target():
            pass

        class Sample:
            def on_target(self):
                pass

        sample = Sample()

        return events.ListenerSet((on_target, sample.on_target))

    def test_repr(self, target: events.ListenerSet):
        actual = repr(target)
        assert (
            actual == "ListenerSet("
            "TestListenerSet.target.<locals>.Sample.on_target, "
            "TestListenerSet.target.<locals>.on_target)"
        )

    def test_iadd__listener(self, target: events.ListenerSet):
        def on_target():
            pass

        target += on_target

        assert (
            repr(target) == "ListenerSet("
            "TestListenerSet.target.<locals>.Sample.on_target, "
            "TestListenerSet.target.<locals>.on_target, "
            "TestListenerSet.test_iadd__listener.<locals>.on_target)"
        )

    def test_iadd__listener_set(self, target: events.ListenerSet):
        def on_target():
            pass

        listeners = events.ListenerSet((on_target,))

        target += listeners

        assert (
            repr(target) == "ListenerSet("
            "TestListenerSet.target.<locals>.Sample.on_target, "
            "TestListenerSet.target.<locals>.on_target, "
            "TestListenerSet.test_iadd__listener_set.<locals>.on_target)"
        )

    def test_tap(self, target: events.ListenerSet):
        def on_target():
            pass

        with target.tap(on_target):
            assert (
                repr(target) == "ListenerSet("
                "TestListenerSet.target.<locals>.Sample.on_target, "
                "TestListenerSet.target.<locals>.on_target, "
                "TestListenerSet.test_tap.<locals>.on_target)"
            )

        assert (
            repr(target) == "ListenerSet("
            "TestListenerSet.target.<locals>.Sample.on_target, "
            "TestListenerSet.target.<locals>.on_target)"
        )

    def test_call(self):
        actual = []
        target = events.ListenerSet()

        @events.listen_to(target)
        def on_target(value):
            actual.append(value)

        target("foo")
        target("bar")

        assert actual == ["foo", "bar"]


class TestEvent:
    def test_get(self):
        class MyObject:
            target = events.Event[Callable[[], None]]()

        instance = MyObject()

        def on_target():
            pass

        instance.target += on_target

        assert len(instance.target) == 1

    def test__when_object_has_slots(self):
        class MyObject:
            __slots__ = ("foo",)

            target = events.Event[Callable[[], None]]()

        with pytest.raises(TypeError):
            str(MyObject().target)


class TestAsyncListenerSet:
    @pytest.mark.asyncio
    async def test_call(self):
        actual = []
        target = events.AsyncListenerSet()

        @events.listen_to(target)
        async def on_target(value):
            actual.append(value)

        await target("foo")
        await target("bar")

        assert actual == ["foo", "bar"]

    @pytest.mark.asyncio
    async def test_call__no_listeners(self):
        target = events.AsyncListenerSet()

        await target("foo")


class TestAsyncEvent:
    def test_get(self):
        class MyObject:
            target = events.AsyncEvent[Callable[[], Awaitable]]()

        instance = MyObject()

        async def on_target():
            pass

        instance.target += on_target

        assert len(instance.target) == 1


class TestCallbackBinding:
    def test_iadd(self):
        target = events.CallbackBinding()

        def on_target():
            pass

        target += on_target

        assert target._callback is on_target

    def test_bind(self):
        target = events.CallbackBinding()

        def on_target():
            pass

        target.bind(on_target)

        assert target._callback is on_target

        target.unbind()

        assert target._callback is None

    def test_call__bound(self):
        actual = []

        target = events.CallbackBinding()

        @events.bind_to(target)
        def on_target(*args, **kwargs):
            actual.extend((args, kwargs))

        target("a", "b", c="d", e="f")

        assert actual == [("a", "b"), {"c": "d", "e": "f"}]

    def test_call__unbound(self):
        # Should just do nothing
        target = events.CallbackBinding()

        target("a", "b", c="d", e="f")


class TestCallback:
    def test_get(self):
        class MyObject:
            target = events.Callback[Callable[[], None]]()

        instance = MyObject()

        @events.bind_to(instance.target)
        def on_target():
            pass

        target = instance.target
        assert target._callback is on_target

    def test_call(self):
        class MyObject:
            target = events.Callback[Callable[[], str]]()

        instance = MyObject()

        @events.bind_to(instance.target)
        def on_target():
            return "foo"

        actual = instance.target()

        assert actual == "foo"

    def test__when_object_has_slots(self):
        class MyObject:
            __slots__ = ("foo",)

            target = events.Callback[Callable[[], None]]()

        with pytest.raises(TypeError):
            str(MyObject().target)


class TestAsyncCallbackBinding:
    def test_call__bound(self, event_loop):
        actual = []

        target = events.AsyncCallbackBinding()

        @events.bind_to(target)
        async def on_target(*args, **kwargs):
            actual.extend((args, kwargs))

        event_loop.run_until_complete(target("a", "b", c="d", e="f"))

        assert actual == [("a", "b"), {"c": "d", "e": "f"}]

    def test_call__unbound(self, event_loop):
        # Should just do nothing
        target = events.AsyncCallbackBinding()

        event_loop.run_until_complete(target("a", "b", c="d", e="f"))


class TestAsyncCallback:
    def test_get(self):
        class MyObject:
            target = events.AsyncCallback[Callable[[], Awaitable]]()

        instance = MyObject()

        @events.bind_to(instance.target)
        async def on_target():
            pass

        target = instance.target
        assert target._callback is on_target
