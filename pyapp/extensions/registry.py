import importlib

from typing import Optional, Callable, Sequence, List, Dict

from pyapp.conf import settings, factory as loader_factory
from pyapp.conf.loaders import Loader
from pyapp.utils import cached_property

__all__ = ("registry", "load", "Extension")


class Extension:
    """
    Wrapper that provides accessors to extension module values.
    """

    def __init__(self, module, package):
        self.module = module
        self.package = package

    def summary(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "version": self.version,
            "package": self.package,
            "checks": self.checks_module,
            "default_settings": self.default_settings,
        }

    def trigger_ready(self):
        """
        Trigger the ready callback to indicate extensions have been loaded and marked as ready.
        """
        if self.ready_callback:
            self.ready_callback()

    def _resolve_name(self, name: str) -> Optional[str]:
        """
        Return the absolute name of the module to be imported.
        """
        if isinstance(name, str):
            if name.startswith("."):
                return self.package + name
            return name

    @cached_property
    def name(self) -> str:
        """
        Name of the extension
        """
        return self.module.__name__

    @cached_property
    def version(self) -> str:
        """
        Version of the extension
        """
        return getattr(self.module, "__version__", None)

    @cached_property
    def checks_module(self) -> str:
        """
        Module used to provide checks.
        """
        return self._resolve_name(getattr(self.module, "__checks__", None))

    @cached_property
    def default_settings(self) -> str:
        """
        Default settings module.
        """
        return self._resolve_name(getattr(self.module, "__default_settings__", None))

    @cached_property
    def ready_callback(self) -> Callable[[], None]:
        """
        Callback executed when all extensions are loaded and ready.
        """
        return getattr(self.module, "ready", None)


class ExtensionRegistry(List[Extension]):
    """
    Registry for tracking install PyApp extensions.
    """

    def load(self, module_name: str):
        """
        Load a module

        :param module_name: Name of the module to load (in standard python dot format)
        :raises: ImportError

        """
        module = importlib.import_module(module_name)
        if module not in self:
            self.append(Extension(module, module_name))

    def load_from_settings(self):
        """
        Load all extensions defined in settings
        """
        for module_name in settings.EXT:
            self.load(module_name)

    def summary(self) -> Sequence[Dict[str, str]]:
        """
        Returns a summary of the loaded extension modules.
        """
        return tuple(ext.summary() for ext in self)

    def trigger_ready(self):
        """
        Trigger ready callback on all extension modules.
        """
        for extension in self:
            extension.trigger_ready()

    @property
    def settings_loaders(self) -> Sequence[Loader]:
        """
        Return a list of module loaders for extensions that specify default settings.
        """
        return tuple(
            loader_factory(module.default_settings)
            for module in self
            if module.default_settings
        )

    @property
    def check_locations(self) -> Sequence[str]:
        """
        Return a list of checks modules for extensions that specify checks.
        """
        return tuple(module.checks_module for module in self if module.checks_module)


# Shortcuts and global extension registry.
registry = ExtensionRegistry()
load = registry.load
