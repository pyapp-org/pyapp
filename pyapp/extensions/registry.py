import pkg_resources

from typing import Sequence, Iterator, Optional, List

from pyapp.app.arguments import CommandGroup

__all__ = ("registry", "ExtensionEntryPoints", "ExtensionWrapper")

ENTRY_POINTS = "pyapp.extensions"


class ExtensionEntryPoints:
    def __init__(self, white_list: Sequence[str] = None):
        self.white_list = white_list

    def _entry_points(self) -> Iterator[pkg_resources.EntryPoint]:
        """
        Iterator of filtered extension entry points
        """
        white_list = self.white_list
        for entry_point in pkg_resources.iter_entry_points(ENTRY_POINTS):
            if white_list is None or entry_point.name in white_list:
                yield entry_point

    def extensions(self) -> Iterator[object]:
        """
        Iterator of loaded extensions.
        """
        for entry_point in self._entry_points():
            yield entry_point.resolve()

    def summary(self):
        """
        List of extensions that are installed (and or while listed)
        """
        for entry_point in self._entry_points():
            print(
                f"Key:\t\t{entry_point.name}\n"
                f"Name:\t\t{entry_point.dist.project_name}\n"
                f"Version:\t{entry_point.dist.version}"
            )


class ExtensionWrapper:
    """
    Wrapper around an extension to provide calling convenience.
    """

    def __init__(self, extension):
        self.extension = extension

    def __repr__(self):
        return repr(self.extension)

    @property
    def default_settings(self) -> str:
        module = getattr(self.extension, "default_settings", "default_settings")
        if module.startswith("."):
            return f"{self.extension.__module__}{module}"
        else:
            return module

    @property
    def checks_module(self) -> Optional[str]:
        """
        Get reference to optional checks module.
        """
        module = getattr(self.extension, "checks", "checks")
        if module and module.startswith("."):
            return f"{self.extension.__module__}{module}"
        else:
            return module

    def register_commands(self, root: CommandGroup):
        if hasattr(self.extension, "register_commands"):
            self.extension.register_commands(root)

    def ready(self):
        if hasattr(self.extension, "ready"):
            self.extension.ready()


class ExtensionRegistry(List[ExtensionWrapper]):
    """
    Registry for tracking install PyApp extensions.
    """

    def load_from(self, extensions: Iterator[object]):
        for extension in extensions:
            self.append(ExtensionWrapper(extension))

    def register_commands(self, root: CommandGroup):
        """
        Trigger ready callback on all extension modules.
        """
        for extension in self:
            extension.register_commands(root)

    def ready(self):
        """
        Trigger ready callback on all extension modules.
        """
        for extension in self:
            extension.ready()

    @property
    def default_settings(self) -> Sequence[str]:
        """
        Return a list of module loaders for extensions that specify default settings.
        """
        return tuple(
            module.default_settings for module in self if module.default_settings
        )

    @property
    def check_locations(self) -> Sequence[str]:
        """
        Return a list of checks modules for extensions that specify checks.
        """
        return tuple(module.checks_module for module in self if module.checks_module)


# Shortcuts and global extension registry.
registry = ExtensionRegistry()
