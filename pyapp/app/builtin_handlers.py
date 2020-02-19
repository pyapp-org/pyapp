# pylint: disable=import-outside-toplevel
"""
App Builtin Handlers
~~~~~~~~~~~~~~~~~~~~

Commands that come builtin to the pyApp CLI.

"""
import sys
from argparse import FileType

from pyapp.app.arguments import argument
from pyapp.app.arguments import CommandGroup


def checks(app):
    """
    Register the checks handler
    """

    @argument(
        "-t",
        "--tag",
        dest="tags",
        action="append",
        help_text="Run checks associated with a tag.",
    )
    @argument(
        "--verbose", dest="verbose", action="store_true", help_text="Verbose output."
    )
    @argument(
        "--out",
        dest="out",
        default=sys.stdout,
        type=FileType(mode="w"),
        help_text="File to output check report to; default is stdout.",
    )
    @argument(
        "--table",
        dest="table",
        action="store_true",
        help_text="Output report in tabular format.",
    )
    @app.command(name="checks", help_text="Run a check report")
    def _handler(opts):
        from pyapp.checks.report import execute_report

        if execute_report(
            opts.out,
            app.application_checks,
            opts.checks_message_level,
            tags=opts.tags,
            verbose=opts.verbose,
            no_color=opts.no_color,
            table=opts.table,
            header=f"Check report for {app.application_summary}",
        ):
            sys.exit(4)


def extensions(app: CommandGroup):
    """
    Register extension report handler
    """

    @argument(
        "--verbose", dest="verbose", action="store_true", help_text="Verbose output."
    )
    @argument(
        "--out",
        dest="out",
        default=sys.stdout,
        type=FileType(mode="w"),
        help_text="File to output extension report to; default is stdout.",
    )
    @app.command(name="extensions")
    def _handler(opts):
        """
        Report of installed PyApp extensions.
        """
        from pyapp.extensions.report import ExtensionReport

        return ExtensionReport(opts.verbose, opts.no_color, opts.out).run()


def settings(app: CommandGroup):
    """
    Register settings report handler
    """

    @argument(
        "--out",
        dest="out",
        default=sys.stdout,
        type=FileType(mode="w"),
        help_text="File to output settings report to; default is stdout.",
    )
    def _handler(opts):
        """
        Report of current settings.
        """
        from pyapp.conf.report import SettingsReport

        return SettingsReport(False, opts.no_color, opts.out).run()

    app.command(_handler, name="settings")
