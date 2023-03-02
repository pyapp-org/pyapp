# pylint: disable=import-outside-toplevel
"""
App Builtin Handlers
~~~~~~~~~~~~~~~~~~~~

Commands that come builtin to the pyApp CLI.

"""
from argparse import FileType, Namespace
from typing import List, Optional

from rich.console import Console

from pyapp.app.arguments import Arg, CommandGroup


def checks(app):
    """
    Register the checks handler
    """

    @app.command(name="checks", help_text="Run a check report")
    def _handler(
        opts: Namespace,
        *,
        tags: List[str] = Arg(
            "-t",
            "--tag",
            help="Run checks associated with a tag.",
        ),
        table: bool = Arg(help="Output report in tabular format."),
        verbose: bool = Arg(help="Verbose output"),
        out: FileType(mode="wt") = Arg(
            default=None,
            help="File to output check report to; default is stdout.",
        ),
    ) -> Optional[int]:
        from pyapp.checks.report import execute_report

        return (
            4
            if execute_report(
                out,
                app.application_checks,
                opts.checks_message_level,
                tags=tags,
                verbose=verbose,
                no_color=opts.no_color,
                table=table,
                header=f"Check report for {app.application_summary}",
            )
            else None
        )


def extensions(app: CommandGroup):
    """
    Register extension report handler
    """

    @app.command(name="extensions")
    def _handler(
        opts: Namespace,
        *,
        verbose: bool = Arg(help="Verbose output"),
        out: FileType(mode="wt") = Arg(
            default=None,
            help="File to output extension report to; default is stdout.",
        ),
    ) -> Optional[int]:
        """
        Report of installed PyApp extensions.
        """
        from pyapp.extensions.report import ExtensionReport

        console = Console(file=out, no_color=opts.no_color)
        return ExtensionReport(console, verbose).run()


def settings(app: CommandGroup):
    """
    Register settings report handler
    """

    def _handler(
        opts: Namespace,
        *,
        out: FileType(mode="wt") = Arg(
            default=None,
            help="File to output settings report to; default is stdout.",
        ),
    ) -> Optional[int]:
        """
        Report of current settings.
        """
        from pyapp.conf.report import SettingsReport

        console = Console(file=out, no_color=opts.no_color)
        return SettingsReport(console).run()

    app.command(_handler, name="settings")
