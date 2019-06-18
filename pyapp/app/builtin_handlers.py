import argparse
import sys

from .arguments import CommandGroup


def extensions(app: CommandGroup):
    from pyapp.app import argument

    # Register extension report handler
    @argument(
        "--verbose", dest="verbose", action="store_true", help_text="Verbose output."
    )
    @argument(
        "--out",
        dest="out",
        default=sys.stdout,
        type=argparse.FileType(mode="w"),
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
    from pyapp.app import argument

    # Register settings report handler
    @argument(
        "--out",
        dest="out",
        default=sys.stdout,
        type=argparse.FileType(mode="w"),
        help_text="File to output settings report to; default is stdout.",
    )
    def _handler(opts):
        """
        Report of current settings.
        """
        from pyapp.conf.report import SettingsReport

        return SettingsReport(False, opts.no_color, opts.out).run()

    app.command(_handler, name="settings")
