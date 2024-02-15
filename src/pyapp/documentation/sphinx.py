"""Sphinx plugin to document elements of PyApp."""
from typing import Any

from sphinx.application import Sphinx
from sphinx.ext.autodoc import ModuleDocumenter

from .settings import SettingsDocumentor


class SettingsDocumenter(ModuleDocumenter):
    """Sphinx autodoc class for documenting settings."""

    objtype = "pyapp-settings"
    directivetype = "module"

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

    def document_members(self, all_members=False):
        """Update the document members section to include settings."""
        settings = SettingsDocumentor(self.object)
        settings.process()

        for group, settings_group in settings.discovered_settings.items():
            if group:
                self.add_line(f"{group}", "<autodoc>")
                self.add_line("=" * len(group), "<autodoc>")

            self.add_line(".. role:: python(code)", "<autodoc>")
            self.add_line("  :language: python", "<autodoc>")
            self.add_line("  :class: highlight", "<autodoc>")
            self.add_line("", "<autodoc>")

            for setting_key, type_name, default, doc in settings_group:
                self.add_line(f"``{setting_key}``", "<autodoc>")

                old_indent = self.indent
                self.indent += self._extra_indent

                if type_name is not None:
                    self.add_line(f"**Type**: :python:`{type_name}`", "<autodoc>")
                    self.add_line("", "<autodoc>")
                self.add_line(f"**Default**: :python:`{default}`", "<autodoc>")
                self.add_line("", "<autodoc>")

                if doc is not None:
                    self.add_block(doc)
                else:
                    self.add_line("", "<autodoc>")

                self.indent = old_indent


def setup(app: Sphinx):
    app.add_autodocumenter(SettingsDocumenter)
    return {"version": "0.1", "parallel_read_safe": True}
