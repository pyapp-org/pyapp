"""
Conf Report
~~~~~~~~~~~

Generates settings reports

"""
from rich.console import Console
from rich.pretty import Pretty
from rich.table import Table

from pyapp import conf


class SettingsReport:
    """Report of all settings in use."""

    def __init__(
        self,
        console: Console,
        verbose: bool = False,
        settings: str = None,
    ):
        """Initialise check report.

        :param console: Console output
        :param verbose: Enable verbose output
        :param settings: Settings to produce a report of.
        """
        self.console = console
        self.verbose = verbose
        self.settings = settings or conf.settings

    def output(self):
        """Output a result to output file."""
        table = Table(title="Settings")
        table.add_column("Setting", style="yellow")
        table.add_column("Value")

        for key, value in self.settings.items():
            table.add_row(key, Pretty(value))

        return table

    def run(self):
        """Run the report."""
        self.console.print(self.output())
