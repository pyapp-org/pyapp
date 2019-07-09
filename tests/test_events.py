from typing import Callable, Awaitable

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


class TestAsyncListenerSet:
    def test_call(self, event_loop):
        actual = []
        target = events.AsyncListenerSet()

        @events.listen_to(target)
        async def on_target(value):
            actual.append(value)

        event_loop.run_until_complete(target("foo"))
        event_loop.run_until_complete(target("bar"))

        assert actual == ["foo", "bar"]

    def test_call__no_listeners(self, event_loop):
        target = events.AsyncListenerSet()

        event_loop.run_until_complete(target("foo"))


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

        def on_target(test):
            pass

        target += on_target

        assert target._callback is on_target
