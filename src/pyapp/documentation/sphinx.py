"""Sphinx plugin to document elements of PyApp."""
from typing import Any

from sphinx.application import Sphinx
from sphinx.ext.autodoc import ModuleDocumenter, bool_option
from sphinx.util.typing import OptionSpec

from .settings import SettingDef, SettingDefGroup, SettingsCollection


class SettingsDocumenter(ModuleDocumenter):
    """Sphinx autodoc class for documenting settings."""

    objtype = "pyapp-settings"
    directivetype = "module"

    option_spec: OptionSpec = {
        "noindex": bool_option,
        "nogroups": bool_option,
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
            self.add_line(line, "<autodoc>")
        self.add_line("", "<autodoc>")

    def document_setting(self, setting: SettingDef):
        """Document a setting definition."""

        self.add_line(f"``{setting.key}``", "<autodoc>")

        old_indent = self.indent
        self.indent += self._extra_indent

        if setting.type_name is not None:
            self.add_line(f"**Type**: :python:`{setting.type_name}`", "<autodoc>")
            self.add_line("", "<autodoc>")
        self.add_line(f"**Default**: :python:`{setting.default}`", "<autodoc>")
        self.add_line("", "<autodoc>")

        if setting.doc is not None:
            self.add_block(setting.doc)
        else:
            self.add_line("", "<autodoc>")

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

        self.add_line(f".. class:: {group.name}", "<autodoc>")
        self.add_line("", "<autodoc>")

        old_indent = self.indent
        self.indent += self._extra_indent

        if group.doc is not None:
            self.add_block(group.doc)
        else:
            self.add_line("", "<autodoc>")

        self.document_group_settings(group)

        self.indent = old_indent

    def document_members(self, all_members=False):
        """Update the document members section to include settings."""
        collection = SettingsCollection(self.object).process()

        # Define a code highlight role
        self.add_line(".. role:: python(code)", "<autodoc>")
        self.add_line("  :language: python", "<autodoc>")
        self.add_line("  :class: highlight", "<autodoc>")
        self.add_line("", "<autodoc>")

        if self.options.get("nogroups", False):
            self.document_group_settings(collection.all_settings)
        else:
            # Do un-grouped first
            self.document_group_settings(collection.settings[None])

            for group in collection.settings.values():
                if group.name is not None:
                    self.document_group(group)


def setup(app: Sphinx):
    app.add_autodocumenter(SettingsDocumenter)
    return {"version": "0.1", "parallel_read_safe": True}
