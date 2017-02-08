from __future__ import absolute_import, unicode_literals

import importlib

from pyapp.conf import settings, factory


class ExtensionRegistry(object):
    """
    Registry for tracking install PyApp extensions.
    """
    def __init__(self):
        self._extension_modules = []

    def load(self, module_name):
        """
        Load a module from

        :param module_name: Name of the module to load (in standard python dot format)
        :raises: ImportError

        """
        module = importlib.import_module(module_name)
        if module not in self._extension_modules:
            self._extension_modules.append(module)

    def load_from_settings(self):
        """
        Load all extensions defined in settings
        """
        for module_name in settings.EXT:
            self.load(module_name)

    def summary(self):
        """
        Returns a summary of the loaded extension modules.
        """
        module_summary = []
        for extension_module in self._extension_modules:
            module_summary.append({
                'name': getattr(extension_module, '__name__'),
                'version':  getattr(extension_module, '__version__', None),
                'checks': getattr(extension_module, '__checks__', None),
                'default_settings': getattr(extension_module, '__default_settings__', None),
            })
        return module_summary

    @property
    def settings_loaders(self):
        """
        Return a list of module loaders for extensions that specify default settings.
        """
        return [
            factory(module.__default_settings__)
            for module in self._extension_modules if getattr(module, '__default_settings__', None)
        ]

    @property
    def check_locations(self):
        """
        Return a list of checks modules for extensions that specify checks.
        """
        return [
            module.__checks__ for module in self._extension_modules if getattr(module, '__checks__', None)
        ]

# Shortcuts and global extension registry.
registry = ExtensionRegistry()
load = registry.load
