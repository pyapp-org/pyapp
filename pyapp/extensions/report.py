"""
Extension Report
~~~~~~~~~~~~~~~~

Generates the report of the currently loaded/available extensions.

"""
import sys

from colorama import Fore
from colorama import Style

from pyapp.extensions.registry import ExtensionDetail
from pyapp.extensions.registry import registry


class ExtensionReport:
    """
    Wrapper for the generation of a check report.
    """

    width = 80

    BASIC_TEMPLATE_MONO = "+ {name} ({version})\n"
    VERBOSE_TEMPLATE_MONO = (
        f"{'=' * width}\n"
        f" Name:       {{name}} ({{key}})\n"
        f" Version     {{version}}\n"
        f" Settings:   {{default_settings}}\n"
        f" Has Checks: {{has_checks}}\n"
        f"{'=' * width}\n\n"
    )
    BASIC_TEMPLATE = (
        f"{Fore.YELLOW}+{Fore.CYAN} {{name}}{Style.RESET_ALL} ({{version}})\n"
    )
    VERBOSE_TEMPLATE = (
        f"{Fore.YELLOW}{'=' * width}{Style.RESET_ALL}\n"
        f"{Style.BRIGHT} Name:       {Style.RESET_ALL}{Fore.CYAN}{{name}} ({{key}}){Style.RESET_ALL}\n"
        f"{Style.BRIGHT} Version:    {Style.RESET_ALL}{Fore.CYAN}{{version}}{Style.RESET_ALL}\n"
        f"{Style.BRIGHT} Settings:   {Style.RESET_ALL}{Fore.CYAN}{{default_settings}}{Style.RESET_ALL}\n"
        f"{Style.BRIGHT} Has Checks: {Style.RESET_ALL}{Fore.CYAN}{{has_checks}}{Style.RESET_ALL}\n"
        f"{Fore.YELLOW}{'=' * width}{Style.RESET_ALL}\n\n"
    )

    def __init__(
        self,
        verbose=False,
        no_color=False,
        f_out=sys.stdout,
        extension_registry=registry,
    ):
        """
        Initialise check report

        :param verbose: Enable verbose output
        :param no_color: Disable colourised output
        :param f_out: File to output report to; default is ``stdout``
        :param extension_registry: Registry to source extensions from; defaults to the builtin registry.

        """
        self.verbose = verbose
        self.f_out = f_out
        self.no_color = no_color
        self.registry = extension_registry

        # Generate templates
        if self.no_color:
            self.basic_template = self.BASIC_TEMPLATE_MONO
            self.verbose_template = self.VERBOSE_TEMPLATE_MONO
        else:
            self.basic_template = self.BASIC_TEMPLATE
            self.verbose_template = self.VERBOSE_TEMPLATE

    def output_result(self, extension: ExtensionDetail):
        """
        Output a result to output file.
        """
        format_args = dict(
            name=extension.name,
            key=extension.key,
            version=extension.version or "Unknown",
            default_settings=extension.default_settings or "None",
            has_checks="Yes" if bool(extension.checks_module) else "No",
        )

        if self.verbose:
            self.f_out.write(self.verbose_template.format(**format_args))
        else:
            self.f_out.write(self.basic_template.format(**format_args))

    def run(self):
        """
        Run the report
        """
        for extension in self.registry:
            self.output_result(extension)
