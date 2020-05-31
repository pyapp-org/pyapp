Using Async Commands
====================

As of pyApp 4.3 command handlers can be defined as Async functions and pyApp will
take care of setting up an event loop call the handler.

.. code-block:: python

    app = CliApplication()

    @app.command
    async def my_command(args):
        pass


This feature is also available to the default handler.
