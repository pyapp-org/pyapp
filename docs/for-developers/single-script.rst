Single Script
=============

As of pyApp 4.4 the CLI application object can be used with a single file (module)
script. This allows quick scripts to make use pyApp functionality and extensions.

Example:

.. code-block:: python

    from pyapp.app import CliApplication

    app = CliApplication()

    @app.command
    def adduser(username: str, *, email: str = None, is_admin: bool = False):
        """
        Add a user
        """
        ...

    if __name__ == "__main__":
        app.dispatch()
