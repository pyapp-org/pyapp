"""Sphinx plugin to document elements of PyApp."""
from typing import Any, Final

from sphinx.application import Sphinx
from sphinx.ext.autodoc import ModuleDocumenter, bool_option
from sphinx.util.typing import OptionSpec

from .settings import SettingDef, SettingDefGroup, SettingsCollection


DOC_SOURCE: Final[str] = "<autodoc-pyapp>"


class SettingsDocumenter(ModuleDocumenter):
    """Sphinx autodoc class for documenting settings."""

    objtype = "pyapp-settings"
    directivetype = "module"

    option_spec: OptionSpec = {
        "noindex": bool_option,
        "grouped": bool_option,
        "sorted": bool_option,
    }

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        """Don't document submodules automatically"""
        return False

    def add_block(self, lines: str):
        """Add a multi-line block of text to the output."""

        for line in lines.strip().splitlines():
            self.add_line(line, DOC_SOURCE)
        self.add_line("", DOC_SOURCE)

    def document_setting(self, setting: SettingDef):
        """Document a setting definition."""

        self.add_line(f"``{setting.key}``", DOC_SOURCE)

        old_indent = self.indent
        self.indent += self._extra_indent

        if setting.type_name is not None:
            self.add_line(f"**Type**: :python:`{setting.type_name}`", DOC_SOURCE)
            self.add_line("", DOC_SOURCE)
        self.add_line(f"**Default**: :python:`{setting.default}`", DOC_SOURCE)
        self.add_line("", DOC_SOURCE)

        if setting.doc is not None:
            self.add_block(setting.doc)
        else:
            self.add_line("", DOC_SOURCE)

        self.indent = old_indent

    def document_group_settings(self, group: SettingDefGroup):
        """Document a group of settings."""

        settings = (
            group.sorted_settings
            if self.options.get("sorted", False)
            else group.settings
        )
        for setting in settings:
            self.document_setting(setting)

    def document_group(self, group: SettingDefGroup):
        """Document a group of settings."""

        self.add_line(f".. class:: {group.name}", DOC_SOURCE)
        self.add_line("", DOC_SOURCE)

        old_indent = self.indent
        self.indent += self._extra_indent

        if group.doc is not None:
            self.add_block(group.doc)
        else:
            self.add_line("", DOC_SOURCE)

        self.document_group_settings(group)

        self.indent = old_indent

    def document_members(self, all_members=False):
        """Update the document members section to include settings."""
        collection = SettingsCollection(self.object).process()

        # Define a code highlight role
        self.add_line(".. role:: python(code)", DOC_SOURCE)
        self.add_line("  :language: python", DOC_SOURCE)
        self.add_line("  :class: highlight", DOC_SOURCE)
        self.add_line("", DOC_SOURCE)

        if self.options.get("grouped", False):
            # Do un-grouped first
            self.document_group_settings(collection.settings[None])

            for group in collection.settings.values():
                if group.name is not None:
                    self.document_group(group)
        else:
            self.document_group_settings(collection.all_settings)


def setup(app: Sphinx):
    app.add_autodocumenter(SettingsDocumenter)
    return {"version": "0.1", "parallel_read_safe": True}
