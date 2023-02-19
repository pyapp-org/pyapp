"""Settings accessor definitions."""
from typing import Any
from typing import Dict
from typing import Mapping
from typing import Tuple


class SettingDescriptor:
    """Descriptor that can access a named setting."""

    __slots__ = ("setting", "default", "data_type")

    def __init__(self, setting, default, data_type):
        self.setting = setting
        self.default = default
        self.data_type = data_type

    def __get__(self, instance, owner):
        from pyapp.conf import settings  # pylint: disable=import-outside-toplevel

        return getattr(settings, self.setting)


class SettingsDefType(type):
    """Typed Settings definition type."""

    def __new__(cls, name: str, bases, dct: Dict[str, Any], *, prefix: str = ""):
        """Generate new type."""

        setting_descriptors = {}
        annotations = dct.get("__annotations__")
        for key, value in dct.items():
            name = f"{prefix}{key}"
            # Settings must be upper case (or constant style)
            if name.isupper():
                setting_descriptors[key] = SettingDescriptor(
                    name, value, annotations.get(key)
                )

        # Update original dict.
        dct.update(setting_descriptors)
        dct["_settings"] = tuple(setting_descriptors)
        dct["_prefix"] = tuple(prefix)

        return super().__new__(cls, name, bases, dct)


class SettingsDef(metaclass=SettingsDefType):
    """Typed settings definition."""


NamedConfig = Mapping[str, Mapping[str, Any]]
NamedPluginConfig = Mapping[str, Tuple[str, Mapping[str, Any]]]
