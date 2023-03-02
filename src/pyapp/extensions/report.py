"""
Extension Report
~~~~~~~~~~~~~~~~

Generates the report of the currently loaded/available extensions.

"""
from rich.console import Console, group
from rich.table import Table

from .registry import ExtensionRegistry, registry


class ExtensionReport:
    """
    Wrapper for the generation of a check report.
    """

    def __init__(
        self,
        console: Console,
        verbose: bool = False,
        extension_registry: ExtensionRegistry = registry,
    ):
        """
        Initialise check report

        :param console: Console output
        :param verbose: Enable verbose output
        :param extension_registry: Registry to source extensions from; defaults to the builtin registry.

        """
        self.console = console
        self.verbose = verbose
        self.registry = extension_registry

    @group()
    def output(self):
        """Generate output."""
        yield from self.registry

    def verbose_output(self):
        """Generate verbose output."""
        table = Table(title="Extensions")

        table.add_column("Name", style="bright_blue")
        table.add_column("Version", style="cyan")
        table.add_column("Settings", style="yellow")
        table.add_column("Has Checks")

        for extension in self.registry:
            table.add_row(
                f"{extension.name} ({extension.key})",
                extension.version or "Unknown",
                extension.default_settings or "",
                "[green]Yes" if bool(extension.checks_module) else "[orange]No",
            )

        return table

    def run(self):
        """Run the report."""
        self.console.print(self.verbose_output() if self.verbose else self.output())
