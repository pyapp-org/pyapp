"""
Extension Registry
~~~~~~~~~~~~~~~~~~

Central location for registering and obtaining information about registered
extensions.

"""
try:
    import importlib_metadata as metadata
except ImportError:
    from importlib import metadata
from typing import Iterator
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence

from pyapp.app.arguments import CommandGroup

__all__ = ("registry", "ExtensionRegistry", "ExtensionEntryPoints", "ExtensionDetail")

ENTRY_POINTS = "pyapp.extensions"


class ExtensionDetail(NamedTuple):
    """
    Details of an entry point Extension
    """

    extension: object
    key: str
    name: str
    version: str

    def __rich__(self):
        return f"[yellow]+ [cyan]{self.name}[/cyan] ({self.version or 'Unknown'})"

    @property
    def default_settings(self) -> Optional[str]:
        """
        Get reference to optional default settings.
        """
        module = getattr(self.extension, "default_settings", None)
        if module and module.startswith("."):
            return f"{self.extension.__module__}{module}"
        return module

    @property
    def checks_module(self) -> Optional[str]:
        """
        Get reference to optional checks module.
        """
        module = getattr(self.extension, "checks", None)
        if module and module.startswith("."):
            return f"{self.extension.__module__}{module}"
        return module

    def register_commands(self, root: CommandGroup):
        """
        Call an extension to register commands with a command group; if the extension
        provides a the callback point.
        """
        if hasattr(self.extension, "register_commands"):
            self.extension.register_commands(root)

    def ready(self):
        """
        Generate a ready event to an extension; if the extension provides a callback
        point.
        """
        if hasattr(self.extension, "ready"):
            self.extension.ready()


class ExtensionEntryPoints:
    """
    Identifies and loads extensions.
    """

    def __init__(self, allow_list: Sequence[str] = None):
        self.allow_list = allow_list

    def _entry_points(self) -> Iterator[metadata.EntryPoint]:
        """
        Iterator of filtered extension entry points
        """
        entry_points = metadata.entry_points(group=ENTRY_POINTS)
        allow_list = self.allow_list
        if allow_list is None:
            yield from entry_points
        else:
            yield from (
                entry_point
                for entry_point in entry_points
                if entry_point.name in allow_list
            )

    def extensions(self, load: bool = True) -> Iterator[object]:
        """
        Iterator of loaded extensions.
        """
        for entry_point in self._entry_points():
            yield ExtensionDetail(
                entry_point.load() if load else None,
                entry_point.name,
                entry_point.dist.name,
                entry_point.dist.version,
            )


# TODO: Remove when pylint handles typing.List correctly  pylint: disable=fixme
# pylint: disable=not-an-iterable,no-member
class ExtensionRegistry(List[ExtensionDetail]):
    """
    Registry for tracking install PyApp extensions.
    """

    def load_from(self, extensions: Iterator[ExtensionDetail]):
        """
        Load specified extensions from the supplied iterable of Extension Details.
        """
        for extension in extensions:
            self.append(extension)

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
registry = ExtensionRegistry()  # pylint: disable=invalid-name
