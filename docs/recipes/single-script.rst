Single Script
=============

As of pyApp 4.4 the CLI application object can be used with a single file (module)
script. This allows quick scripts to make use pyApp functionality and extensions.

A complete example below making use of SQLAlchemy:

.. code-block:: python

    from pyapp.app import CliApplication
    from pyapp_ext.sqlalchemy import get_connection

    app = CliApplication()

    @app.command
    def adduser(username: str, *, email: str = None, is_admin: bool = False):
        """
        Add a user
        """
        ...

    if __name__ == "__main__":
        app.dispatch()

