"""Helper methods for testing.

Includes a plugin for Pytest.
"""

from types import ModuleType
from collections.abc import Sequence

from ..conf.loaders import settings_iterator


def settings_in_module(
    *modules: ModuleType,
    exclude: Sequence[str] = ("INCLUDE_SETTINGS",),
):
    """Generate a list of settings defined in a module (or modules).

    Used for ensuring that a second settings module only contains specified settings.
    """
    settings = set()

    for mod in modules:
        settings.update(
            name for name, _ in settings_iterator(mod) if name not in exclude
        )

    return settings
