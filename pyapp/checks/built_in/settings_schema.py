from pydantic import BaseConfig, PydanticValueError, PydanticTypeError
from pydantic.typing import AnyCallable
from pydantic.validators import find_validators
from typing import Dict, Sequence, Any, Tuple

from pyapp.conf import Loader, Settings
from ..messages import CheckMessage, Error, Warn


class SettingsSchema(Dict[str, Tuple[Loader, Sequence[AnyCallable]]]):
    """
    Generate a schema file for a settings module.
    """

    def append_loader(self, loader: Loader) -> None:
        """
        Append a loader to the schema.
        """
        warnings = []

        for name, value, type_ in loader:
            validators = list(find_validators(type_, BaseConfig))

            existing = self.get(name)
            if existing:
                warnings.append(
                    f"Setting name `{name}` {loader} already defined in {existing[0]}"
                )
            else:
                self[name] = (loader, validators)

        if warnings:
            raise RuntimeWarning(warnings)

    def validate(self, key: str, v: Any):
        """
        """
        loader, validators = self[key]
        for validator in validators:
            validator(v)


def settings_schema(settings: Settings, **_) -> Sequence[CheckMessage]:
    """
    Checking settings
    """
    messages = []

    # Build a schema from loaders
    schema = SettingsSchema()
    for loader in settings.default_loaders:
        schema.append_loader(loader)

    # Validate settings
    for key, value in ((k, getattr(settings, k)) for k in dir(settings) if k.isupper()):
        # Ignore expected auto generated entries
        if key in ("LOGGING", "SETTINGS_SOURCES"):
            continue

        try:
            schema.validate(key, value)
        except KeyError:
            messages.append(
                Warn(
                    f"Unknown value {key}.",
                    hint="This value is not defined in the setting schema and could be miss-spelled.",
                )
            )
        except (PydanticTypeError, PydanticValueError) as ex:
            messages.append(Error(f"Invalid value {key}.", hint=str(ex)))

    return messages
