"""
Checks Report
~~~~~~~~~~~~~

Generates and execute a report after executing checks.

"""
import csv
import io
import logging
import sys
from io import StringIO
from typing import Any
from typing import Optional
from typing import Sequence
from typing import Union

from colorama import Back
from colorama import Fore
from colorama import Style

from pyapp.checks.registry import Check
from pyapp.checks.registry import CheckMessage
from pyapp.checks.registry import CheckRegistry
from pyapp.checks.registry import import_checks
from pyapp.checks.registry import registry
from pyapp.utils import wrap_text

COLOURS = {
    # Type: (Title, Border),
    logging.CRITICAL: (Fore.WHITE + Back.RED, Fore.RED),
    logging.ERROR: (Fore.RED, Fore.RED),
    logging.WARNING: (Fore.YELLOW, Fore.YELLOW),
    logging.INFO: (Fore.CYAN, Fore.CYAN),
    logging.DEBUG: (Fore.MAGENTA, Fore.MAGENTA),
}


def get_check_name(obj: Any) -> str:
    """
    Get the name of a check
    """
    check = obj.checks if hasattr(obj, "checks") else obj
    return getattr(check, "check_name", check.__name__).format(obj=obj)


class BaseReport:
    """
    Common base class of reports
    """

    def __init__(self, f_out=sys.stdout, check_registry: CheckRegistry = registry):
        """
        :param f_out: File to output report to; default is ``stdout``
        :param check_registry: Registry to source checks from; defaults to the builtin registry.
        """
        self.f_out = f_out
        self.registry = check_registry

    def render_header(self):
        """
        Render any header.
        """

    def render_result_prefix(self, check: Check):
        """
        Called prior to rendering a checks messages
        """

    def render_result(self, check: Check, message: Optional[CheckMessage]):
        """
        Render result of check.
        """

    def render_result_suffix(self, check: Check, message_shown: bool):
        """
        Called after rendering a checks messages.

        Shown indicates if any messages where shown (could be filtered)

        """

    def render_footer(self):
        """
        Render any footer
        """

    def run(
        self, message_level: int = logging.INFO, tags: Sequence[str] = None
    ) -> bool:
        """
        Run the report

        :param message_level: Level of message to be displayed.
        :param tags: List of tags to include in report
        :return: Indicate if any serious message where generated.

        """
        serious_message = False

        self.render_header()

        # Generate report
        for check, messages in self.registry.run_checks_iter(
            tags, self.render_result_prefix
        ):
            message_shown = False
            if messages:
                for message in messages:
                    serious_message = serious_message or message.is_serious()

                    # Filter output
                    if message.level >= message_level:
                        message_shown = True
                        self.render_result(check, message)

            if not message_shown:
                self.render_result(check, None)

            self.render_result_suffix(check, message_shown)

        self.render_footer()

        return serious_message


class CheckReport(BaseReport):
    """
    Wrapper for the generation of a check report.
    """

    width = 80

    def __init__(
        self,
        verbose: bool = False,
        no_color: bool = False,
        header: str = None,
        f_out=sys.stdout,
        check_registry=registry,
    ):
        """
        Initialise check report

        :param verbose: Enable verbose output
        :param no_color: Disable colourised output
        :param header: An optional header to prepend to report (if verbose)
        :param f_out: File to output report to; default is ``stdout``
        :param check_registry: Registry to source checks from; defaults to the builtin registry.

        """
        self.verbose = verbose
        self.no_color = no_color
        self.header = header
        super().__init__(f_out, check_registry)

        # Generate templates
        if self.no_color:
            self.verbose_check_template = "+ {name}\n"
            self.title_template = " {level}: {title}"
            self.hint_template = ("-" * self.width) + "\n HINT: {hint}\n"
            self.message_template = (
                f"{'=' * self.width}\n{{title}}\n{{hint}}{'=' * self.width}\n\n"
            )

        else:
            self.verbose_check_template = (
                f"{Fore.YELLOW}+ {Fore.CYAN}{{name}}{Style.RESET_ALL}\n"
            )
            self.title_template = f"{{style}} {Style.BRIGHT}{{level:7s}}{Style.NORMAL} {{title}}{Style.RESET_ALL}"
            self.hint_template = (
                f"{{border_style}}{'-' * self.width}{Style.RESET_ALL}\n "
                f"{Style.BRIGHT}HINT:{Style.DIM} {Fore.WHITE}{{hint}}{Style.RESET_ALL}\n"
            )
            self.message_template = (
                f"{{border_style}}{'=' * self.width}{Style.RESET_ALL}\n"
                f"{{title}}\n{{hint}}"
                f"{{border_style}}{'=' * self.width}{Style.RESET_ALL}\n\n"
            )

    def render_header(self):
        """
        Render report header
        """
        if self.header and self.verbose:
            self.f_out.write(self.header + "\n")

    def render_result_prefix(self, check: Check):
        """
        Render preface before a result.

        This is used to display a reports name etc.
        """
        if self.verbose:
            self.f_out.write(
                self.verbose_check_template.format(name=get_check_name(check))
            )

    def format_title(self, message: CheckMessage) -> str:
        """
        Format the title of message.
        """
        # Get strings
        level_name = message.level_name
        msg = message.msg
        if message.obj:
            msg = f"{message.obj} - {msg}"

        if self.no_color:
            title_style = ""
            line_sep = "\n"
        else:
            title_style = COLOURS[message.level][0]
            line_sep = Style.RESET_ALL + "\n" + title_style

        return self.title_template.format(
            style=title_style,
            level=level_name,
            title=wrap_text(msg, self.width, indent=9, line_sep=line_sep).lstrip(),
        )

    def format_hint(self, message: CheckMessage) -> str:
        """
        Format the hint of a message.
        """
        hint = message.hint

        if hint:
            # Normalise to a list
            if not isinstance(hint, (list, tuple)):
                hint = (hint,)

            if self.no_color:
                line_sep = "\n"
                border_style = ""
            else:
                line_sep = Style.RESET_ALL + "\n" + Style.DIM + Fore.WHITE
                border_style = COLOURS[message.level][1]

            return self.hint_template.format(
                border_style=border_style,
                hint="\n\n".join(
                    wrap_text(p, self.width, indent=8, line_sep=line_sep) for p in hint
                ).lstrip(),
            )

        return ""

    def render_result(self, _: Check, message: Optional[CheckMessage]):
        if message:
            format_args = dict(
                level=logging.getLevelName(message.level),
                title=self.format_title(message),
                hint=self.format_hint(message),
            )
            if not self.no_color:
                format_args.update(border_style=COLOURS[message.level][1])

            self.f_out.write(self.message_template.format(**format_args))

    def render_result_suffix(self, check: Check, message_shown: bool):
        if not (self.verbose or message_shown):
            self.f_out.write(".\n")


class TabularCheckReport(BaseReport):
    """
    Generation of a check report that outputs tabular output.
    """

    def __init__(
        self, f_out: StringIO = sys.stdout, check_registry: CheckRegistry = registry
    ):
        """
        Initialise report
        """
        super().__init__(f_out, check_registry)
        self.writer = csv.writer(self.f_out, delimiter=str("\t"))

    def render_result(self, check: Check, message: Optional[CheckMessage]):
        name = get_check_name(check)
        if message:
            self.writer.writerow([name, message.level_name, message.msg])
        else:
            self.writer.writerow([name, "OK", ""])


def execute_report(
    output: io.StringIO,
    application_checks: str,
    message_level: Union[str, int] = logging.INFO,
    tags: Sequence[str] = None,
    verbose: bool = False,
    no_color: bool = False,
    table: bool = False,
    header: str = None,
) -> bool:
    """
    Run application checks.

    :param output: File like object to write output to.
    :param message_level: Reporting level.
    :param application_checks: Application builtin check module
    :param tags: Specific tags to run.
    :param verbose: Display verbose output.
    :param no_color: Disable coloured output.
    :param table: Tabular output (disables verbose and colour option)
    :param header: Header message for standard report

    """
    # Import default application checks
    try:
        __import__(application_checks)
    except ImportError:
        pass

    # Import additional checks defined in settings.
    import_checks()

    # Note the getLevelName method returns the level code if a string level is supplied!
    if isinstance(message_level, str):
        message_level = logging.getLevelName(message_level)

    # Create report instance
    if table:
        return TabularCheckReport(output).run(message_level, tags)

    return CheckReport(verbose, no_color, header, output).run(message_level, tags)
