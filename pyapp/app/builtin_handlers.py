import argparse
import sys


def extensions(app):
    from pyapp.app import argument

    # Register extension report handler
    @argument("--verbose", dest="verbose", action="store_true", help="Verbose output.")
    @argument(
        "--out",
        dest="out",
        default=sys.stdout,
        type=argparse.FileType(mode="w"),
        help="File to output extension report to; default is stdout.",
    )
    def _handler(opts, **_):
        """
        Report of installed PyApp extensions.
        """
        from pyapp.extensions.report import ExtensionReport

        return ExtensionReport(opts.verbose, opts.no_color, opts.out).run()

    app.command(_handler, cli_name="extensions")


def settings(app):
    from pyapp.app import argument

    # Register settings report handler
    @argument(
        "--out",
        dest="out",
        default=sys.stdout,
        type=argparse.FileType(mode="w"),
        help="File to output settings report to; default is stdout.",
    )
    def _handler(opts, **_):
        """
        Report of current settings.
        """
        from pyapp.conf.report import SettingsReport

        return SettingsReport(False, opts.no_color, opts.out).run()

    app.command(_handler, cli_name="settings")
