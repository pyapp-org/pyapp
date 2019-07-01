"""
Extensions
~~~~~~~~~~

*Extensions allow for additional features to be added to pyApp.*

With pyApp 4.0 the extension interface was redesigned to allow for extensions a lot
more flexibility in what they can do.

Extensions can:

- Provide default settings
- Register checks
- Add commands to the CLI
- Register factories with the injection framework.

.. note:: Extensions developed for previous versions of pyApp need to be upgraded
          to work with pyApp 4.


Using extensions
----------------

Once an extension has been installed it is immediately available in pyApp. The
CLI `extensions` command will list all installed extensions. You will also likely
see additional settings files being loaded on startup.

Control of the extension version and availability of extensions is left up to the
standard packaging tools and processes. I would recommend using
`pipenv <https://docs.pipenv.org/en/latest/>`_ to control this. If you project has
specific security requirements a whitelist can be provided to `CliApplication` to
only allow specific extensions to be loaded.


Developing an extension
-----------------------

An extension is a normal Python package with some specific criteria.

Extensions must provide a `setuptools` entry point, this is how they are identified
by pyApp and loaded.

In a `setup.py` file::

    setup(
        ...
        entry_points={'pyapp.extensions': 'my-extension = my_extension:Extension'}
        ...
    )

or in a `setup.cfg` file::

    [options.entry_points]
    pyapp.extensions =
        my-extension = my_extension:Extension


You can use any name you wish (or provide multiple entry points) for the extension.
The entry `my_extension:Extension` refers to a class called `Extension` in the
`my_extension` package.

The extension class requires no base and duck typing is used to look for specific
functionality.

The following attributes/methods are used by pyApp:

`default_settings`
    A string that specifies a module that provides default settings.

`checks`
    A string that specifies a module that registers additional checks.

`def register_commands(root: CommandGroup)`
    A method that is called at startup to allow the extension to register additional
    commands. This happens early in the startup process prior to settings being
    loaded.

`def ready()`
    The application has been successfully started and is ready. This is an opportunity
    to register any custom functionality with pyApp.


An example extension class::

    class Extension:
        default_settings = ".default_settings"
        checks = ".checks"

        @staticmethod
        def register_commands(root: CommandGroup):
            # Register a group and commands
            group = root.create_command_group("foo")

            @group.command
            def bar(opts):
                '''
                Do a foo bar operation.
                '''

        @staticmethod
        def ready():
            pass
"""
from .registry import *
