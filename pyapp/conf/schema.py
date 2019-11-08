from pydantic import BaseConfig, PydanticValueError, PydanticTypeError
from pydantic.typing import AnyCallable
from pydantic.validators import find_validators
from typing import Dict, Sequence, Any, Tuple

from pyapp.conf import Loader


class SchemaError(RuntimeError):
    """
    Common base exception type
    """


class ValidationError(SchemaError):
    """
    Collection of errors from validation rules
    """
    def __init__(self, key: str, loader: Loader, errors: Sequence[str]):
        self.key = key
        self.loader = loader
        self.errors = errors

    def __str__(self):
        return f"{self.key} ({self.loader}) " + ", ".join(self.errors)


class UnknownSetting(SchemaError, KeyError):
    """
    Setting name was not found in schema
    """


class SettingsSchemaConfig(BaseConfig):
    """
    Customised schema config
    """
    arbitrary_types_allowed = False


class SettingsSchema(Dict[str, Tuple[Loader, Sequence[AnyCallable]]]):
    """
    Generate a schema file for a settings module.
    """

    def append_loader(self, loader: Loader) -> Sequence[str]:
        """
        Append a loader to the schema.

        Returns a list of warnings, not necessarily bad but could be an issue.

        """
        warnings = []

        for name, value, type_ in loader:
            existing = self.get(name)
            if existing:
                warnings.append(
                    f"Setting name `{name}` {loader} already defined in {existing[0]}"
                )
            else:
                validators = list(find_validators(type_, SettingsSchemaConfig))
                self[name] = (loader, validators)

        return warnings

    def validate_value(self, key: str, value: Any):
        """
        Validate a particular schema value
        """
        try:
            loader, validators = self[key]
        except KeyError:
            raise UnknownSetting(f"Setting {key} was not found in schema.")

        errors = []
        for validator in validators:
            try:
                validator(value)
            except (PydanticTypeError, PydanticValueError) as ex:
                errors.append(str(ex))

        if errors:
            raise ValidationError(key, loader, errors)
