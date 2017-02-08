from __future__ import print_function, unicode_literals

import sys
import textwrap

from pyapp.extentions.registry import registry

try:
    import colorama
except ImportError:
    colorama = None
else:
    from colorama import Style, Fore, Back


class ExtensionReport(object):
    """
    Wrapper for the generation of a check report.
    """
    def __init__(self, verbose=False, no_color=False, f_out=sys.stdout, extension_registry=registry, width=80):
        """
        Initialise check report

        :param verbose: Enable verbose output
        :param no_color: Disable colourised output (if colorama is installed)
        :param f_out: File to output report to; default is ``stdout``
        :param extension_registry: Registry to source extensions from; defaults to the builtin registry.
        :param width: Width of output.

        """
        self.verbose = verbose
        self.f_out = f_out
        # Default color to be disabled if colorama is not installed.
        self.no_color = no_color if colorama else True
        self.registry = extension_registry
        self.width = width

        # Generate templates
        if self.no_color:
            self.TEMPLATE = ("=" * self.width) + \
                            "\n {name}\n" + \
                            "\n Version: {version}\n" + \
                            ("-" * self.width) + \
                            "\n\n" + \
                            ("=" * self.width)

        else:
            self.TEMPLATE = Fore.YELLOW + ("=" * self.width) + Style.RESET_ALL + \
                            "\n {name}\n" + \
                            "\n Version: {version} \n" + \
                            Fore.YELLOW + ("-" * self.width) + Style.RESET_ALL + \
                            "\n \n" + \
                            Fore.YELLOW + ("-" * self.width) + Style.RESET_ALL

    def wrap_text(self, text, indent_width, line_sep='\n'):
        """
        Perform word wrapping on text

        :param text: Text to wrap.
        :type text: str
        :indent_width indent: Size of text indent.
        :type indent_width: int
        :param line_sep: Line separator
        :rtype: str

        """
        indent = ' ' * (indent_width + 1)
        lines = textwrap.wrap(
            text, self.width - 2,
            initial_indent=indent, subsequent_indent=indent
        )
        return line_sep.join(l + (' ' * (self.width - len(l))) for l in lines)

    def format_title(self, message):
        """
        Format the title of message.
        """
        # Get strings
        level_name = logging.getLevelName(message.level)
        msg = message.msg
        if message.obj:
            msg = "{} - {}".format(message.obj, msg)

        if self.no_color:
            title_style = ''
            line_sep = "\n"
        else:
            title_style = COLOURS[message.level][0]
            line_sep = Style.RESET_ALL + "\n" + title_style

        return self.TITLE_TEMPLATE.format(
            style=title_style, level=level_name,
            title=self.wrap_text(msg, len(level_name) + 2, line_sep).lstrip()
        )

    def format_hint(self, message):
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

            indent_width = len(" Hint: ")
            return self.HINT_TEMPLATE.format(
                border_style=border_style,
                hint='\n\n'.join(self.wrap_text(p, indent_width, line_sep) for p in hint).lstrip()
            )
        else:
            return ''

    def output_result(self, extension):
        """
        Output a result to output file.

        :type extension: pyapp.extensions.register.Extension

        """
        format_args = dict(
            name=extension.name,
            version=extension.version or 'Unknown',
        )

        self.f_out.write(self.TEMPLATE.format(**format_args))

    def run(self):
        """
        Run the report
        """
        for extension in self.registry:
            self.output_result(extension)
