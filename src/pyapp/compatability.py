"""
Compatibility between Python Releases
"""
__all__ = ("async_run",)

try:
    from asyncio import run as async_run

except ImportError:
    from asyncio import events, coroutines

    def async_run(main):
        """
        A simplified version of Python 3.7+ run
        """
        if events._get_running_loop() is not None:  # pylint: disable=protected-access
            raise RuntimeError(
                "asyncio.run() cannot be called from a running event loop"
            )

        if not coroutines.iscoroutine(main):
            raise ValueError("a coroutine was expected, got {!r}".format(main))

        loop = events.new_event_loop()
        try:
            events.set_event_loop(loop)
            return loop.run_until_complete(main)
        finally:
            events.set_event_loop(None)
            loop.close()
