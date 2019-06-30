import asyncio

from typing import Callable, Awaitable

from pyapp.events import Event, AsyncEvent


class MyClass:
    started = Event[Callable[[], None]]()
    new_message = AsyncEvent[Callable[[str, "MyClass"], Awaitable]]()

    def start(self):
        self.started.trigger()

    async def process_message(self, message):
        await self.new_message.trigger(message, self)


instance = MyClass()


def on_started():
    print("Started: 1...")


instance.started += on_started


def on_another_started():
    print("Started: 2...")


instance.started += on_another_started


async def on_new_message(message: str, source: MyClass):
    print(message)


instance.new_message += on_new_message


instance.start()
aw = instance.process_message("Hi!")
asyncio.get_event_loop().run_until_complete(aw)
