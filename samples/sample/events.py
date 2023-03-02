import asyncio
from typing import Awaitable, Callable

from pyapp.events import AsyncEvent, Event, listen_to


class MyClass:
    started = Event[Callable[[], None]]()
    new_message = AsyncEvent[Callable[[str, "MyClass"], Awaitable]]()

    def start(self):
        self.started()

    async def process_message(self, message):
        await self.new_message(message, self)


class ProxyClass:
    new_message = AsyncEvent[Callable[[str, MyClass], Awaitable]]()

    def __init__(self, my_class: MyClass):
        my_class.new_message += self.new_message


instance = MyClass()
proxy = ProxyClass(instance)


def on_started():
    print("Started: 1...")


instance.started += on_started


@listen_to(instance.started)
def on_another_started():
    print("Started: 2...")


async def on_new_message(message: str, source: MyClass):
    print(message)


instance.new_message += on_new_message
proxy.new_message.add(on_new_message)

instance.start()
aw = instance.process_message("Hi!")
asyncio.get_event_loop().run_until_complete(aw)
