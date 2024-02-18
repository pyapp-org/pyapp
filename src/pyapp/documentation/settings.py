"""Automated settings documentation."""
import ast
from functools import singledispatchmethod
from pathlib import Path
from types import ModuleType
from typing import (
    Any,
    Dict,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Union,
)


class _SettingsExtractor:
    """Used to extract documentation from a default settings modules."""

    def __init__(self, module_or_file: Union[ModuleType, Path, str]):
        if isinstance(module_or_file, ModuleType):
            module_or_file = module_or_file.__file__
        self._file = Path(module_or_file)

        self._current_setting: Optional[Tuple[str, Optional[str], Optional[str]]] = None

    def process(self):
        """Process the settings module or file."""

        content = self._file.read_text(encoding="UTF-8")
        mod = ast.parse(content, self._file)
        self._process_node(mod)

        return self

    def setting(
        self,
        setting_key: str,
        type_name: Optional[str],
        default: Any,
        doc: Optional[str],
    ):
        """Event when a setting is found.

        :param setting_key: Name of the setting key.
        :param type_name: Optional type of the type.
        :param default: Optional default value.
        :param doc: Optional doc string for setting.
        """

    def start_settings_def(self, name: str, doc: Optional[str] = None):
        """Start of settings definition.

        :param name: Name of the settings definition group.
        :param doc: Optional doc string for the settings definition.
        """

    def end_settings_def(self):
        """End of settings definition."""

    def _generate_setting(self, doc: Optional[str] = None):
        """Generate a setting if one is defined."""
        if self._current_setting:
            self.setting(*self._current_setting, doc)
            self._current_setting = None

    @singledispatchmethod
    def _process_node(self, node):
        """Process a node from the settings file."""
        self._generate_setting()

    @_process_node.register
    def _process_module(self, node: ast.Module):
        """Process a module."""
        for item in node.body:
            self._process_node(item)

        # Ensure the last setting is generated
        self._generate_setting()

    @_process_node.register
    def _process_class_definition(self, node: ast.ClassDef):
        """Process a class definition."""

        self._generate_setting()

        if any(
            base.id == "SettingsDef"
            for base in node.bases
            if isinstance(base, ast.Name)
        ):
            self.start_settings_def(node.name, ast.get_docstring(node))
            for item in node.body:
                self._process_node(item)

            self._generate_setting()
            self.end_settings_def()

    @_process_node.register
    def _process_assign(self, node: ast.Assign):
        """Process an assignment."""

        self._generate_setting()

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                self._current_setting = (
                    target.id,
                    None,
                    flatten_default_value(node.value),
                )
                break

    @_process_node.register
    def _process_annotated_assign(self, node: ast.AnnAssign):
        """Process an annotated assignment."""

        self._generate_setting()

        if isinstance(node.target, ast.Name) and node.target.id.isupper():
            self._current_setting = (
                node.target.id,
                flatten_type_annotation(node.annotation),
                flatten_default_value(node.value),
            )

    @_process_node.register
    def _process_expr(self, node: ast.Expr):
        """Process an expression."""
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            self._generate_setting(node.value.value)
        else:
            self._generate_setting()


def flatten_type_annotation(annotation) -> Optional[str]:
    """Flatten a type annotation to a string."""
    if isinstance(annotation, ast.Name):
        return annotation.id

    if isinstance(annotation, ast.Subscript):
        if isinstance(annotation.value, ast.Name) and annotation.value.id == "Union":
            # Compatibility with Python 3.8
            slice_value = (
                annotation.slice.value
                if isinstance(annotation.slice, ast.Index)
                else annotation.slice
            )
            if isinstance(slice_value, ast.Tuple):
                return " | ".join(flatten_type_annotation(v) for v in slice_value.elts)
        return f"{flatten_type_annotation(annotation.value)}"

    return None


def flatten_default_value(value) -> Union[str, int, float, bool, list, dict, None]:
    """Flatten a default value to a string."""

    if isinstance(value, ast.Constant):
        return value.value

    if isinstance(value, ast.Name):
        return value.id

    if isinstance(value, ast.Dict):
        return {k.s: flatten_default_value(v) for k, v in zip(value.keys, value.values)}

    if isinstance(value, (ast.List, ast.Tuple)):
        return [flatten_default_value(v) for v in value.elts]

    return None


class SettingDef(NamedTuple):
    """A setting definition."""

    key: str
    type_name: Optional[str]
    default: Any
    doc: Optional[str]


class SettingDefGroup(NamedTuple):
    """A group of setting definitions."""

    name: Optional[str]
    settings: List[SettingDef]
    doc: Optional[str]

    @property
    def sorted_settings(self) -> List[SettingDef]:
        """Sort settings by key."""
        return sorted(self.settings, key=lambda s: s.key)


class SettingsCollection(_SettingsExtractor):
    """Collect settings from a settings module."""

    def __init__(
        self,
        module_or_file: Union[ModuleType, Path, str],
        *,
        exclude_keys: Sequence[str] = ("INCLUDE_SETTINGS",),
    ):
        super().__init__(module_or_file)
        self.exclude_keys = exclude_keys

        self.current_group: SettingDefGroup = SettingDefGroup(None, [], None)
        self.settings: Dict[Optional[str], SettingDefGroup] = {
            None: self.current_group,
        }

    @property
    def all_settings(self) -> SettingDefGroup:
        """Return all settings ignoring groups."""
        return SettingDefGroup(
            None,
            [setting for group in self.settings.values() for setting in group.settings],
            None,
        )

    def setting(
        self,
        setting_key: str,
        type_name: Optional[str],
        default: Any,
        doc: Optional[str],
    ):
        """Event when a setting is found.

        :param setting_key: Name of the setting key.
        :param type_name: Optional type of the type.
        :param default: Optional default value.
        :param doc: Optional doc string for setting.
        """
        if setting_key not in self.exclude_keys:
            self.current_group.settings.append(
                SettingDef(setting_key, type_name, default, doc)
            )

    def start_settings_def(self, name: str, doc: Optional[str] = None):
        """Start of settings definition.

        :param name: Name of the settings definition group.
        :param doc: Optional doc string for the settings definition.
        """
        self.current_group = _current_group = SettingDefGroup(name, [], doc)
        self.settings[name] = _current_group

    def end_settings_def(self):
        """End of settings definition."""
        self.current_group = self.settings[None]
