"""
Extensions
~~~~~~~~~~

*Provides extensions to pyApp that allows other modules to register checks and default settings.*

Extensions are available via `pyapp.ext` namespace, they are registered with pyApp via a `setuptools`
entry point.

In a `setup.py` file::

    setup(
        ...
        entry_points={'pyapp.extensions': 'my-extension = my_extension'}
        ...
    )

or in a `setup.cfg` file::

    [options.entry_points]
    pyapp.extensions =
        my-extension = my_extension


Extensions then need to be enabled by adding it's name into :py:data:`pyapp.conf.default_settings.EXT`
setting.

Usually extensions will be a python package that contains at least ``default_settings.py``
and ``checks.py`` files. Details of the package can be declared in the ``__init__.py`` file
using the following attributes::

    __name__ = 'Longer name of the Extension`
    __checks__ = '.checks'  # This can be a relative path or fully qualified
    __default_settings__ = '.default_settings'  # This can be a relative path or fully qualified


The ``__checks__`` and ``__default_settings__`` attributes tell PyApp to include these when
loading settings or determining what checks are available.

Use the ``extensions`` command provided by the PyApp CLI to list  extensions (and version)
enabled in or available to your application.


Ready Event
-----------

Once settings have been loaded, logging configured etc a ready callback is triggered to let
the extension perform any initialisation that is required::

    def ready(**_):
        # Do any initialise
        pass


"""
from .registry import *
