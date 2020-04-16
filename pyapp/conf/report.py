"""
Conf Report
~~~~~~~~~~~

Generates settings reports

"""
import pprint
import sys
from typing import TextIO

from colorama import Fore
from colorama import Style

from pyapp import conf
from pyapp.utils import wrap_text


class SettingsReport:
    """
    Report of all settings in use.
    """

    width = 96

    def __init__(
        self,
        verbose: bool = False,
        no_color: bool = False,
        f_out: TextIO = sys.stdout,
        settings: str = None,
    ):
        """
        Initialise check report

        :param verbose: Enable verbose output
        :param no_color: Disable colourised output
        :param f_out: File to output report to; default is ``stdout``
        :param settings: Settings to produce a report of.

        """
        self.verbose = verbose
        self.f_out = f_out
        self.no_color = no_color
        self.settings = settings or conf.settings

        # Generate templates
        if self.no_color:
            self.basic_template = "{key:20} : {ppsetting}\n"

        else:
            self.basic_template = (
                Fore.YELLOW
                + "{key:20} : "
                + Fore.CYAN
                + "{ppsetting}"
                + Style.RESET_ALL
                + "\n"
            )

    def output_result(self, key: str, setting):
        """
        Output a result to output file.
        """
        format_args = dict(
            key=key,
            setting=setting,
            ppsetting=wrap_text(
                pprint.pformat(setting, 2), width=self.width, indent=25
            ).strip(),
        )

        self.f_out.write(self.basic_template.format(**format_args))

    def run(self):
        """
        Run the report
        """
        for key, setting in self.settings.__dict__.items():
            if key.isupper():
                self.output_result(key, setting)
