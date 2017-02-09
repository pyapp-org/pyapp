"""
Extensions
~~~~~~~~~~

*Provides extensions to PyApp that allows other modules to register checks and default settings.*

Extensions are registered with PyApp via the settings file :py:data:`pyapp.conf.default_settings.EXT`
setting. Usually extensions will be a python package that contains at least ``default_settings.py`` and
``checks.py`` files.

Details of the package can be declared in the ``__init__.py`` file using the following attributes::

    __name__ = 'Name of the Extension`
    __version__ = '0.1.0'
    __checks__ = '.checks'  # This can be a relative path or fully qualified
    __default_settings__ = '.default_settings'  # This can be a relative path or fully qualified

The ``__checks__`` and ``__default_settings__`` attributes tell PyApp to include these when loading
 settings or determining what checks are available.

Use the ``extensions`` command provided by the PyApp CLI to list the extensions (and version) installed
in your application.

Ready State
-----------

Once settings have been loaded, logging configured etc a ready callback is triggered to let the extension
perform any initialisation that is required::

    def ready(**_):
        # Do any initialise
        pass

"""
from __future__ import absolute_import

from .registry import *
