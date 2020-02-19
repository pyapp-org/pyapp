"""
App Logger Formatter
~~~~~~~~~~~~~~~~~~~~

Custom formatter for logging messages.

"""
import logging

import colorama

RESET_ALL = colorama.Style.RESET_ALL


class ColourFormatter(logging.Formatter):
    """
    Formatter that adds colourised versions of log levels

    Extends LogRecord with:

    %(clevelno)s        Numeric logging level for the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL) with ANSI terminal colours
                        applied.
    %(clevelname)s      Text logging level for the message ("DEBUG", "INFO",
                        "WARNING", "ERROR", "CRITICAL") with ANSI terminal
                        colours applied.
    """

    COLOURS = {
        logging.CRITICAL: colorama.Fore.RED + colorama.Style.BRIGHT,
        logging.ERROR: colorama.Fore.RED,
        logging.WARNING: colorama.Fore.BLUE,
        logging.INFO: colorama.Fore.GREEN,
        logging.DEBUG: colorama.Fore.LIGHTBLACK_EX,
        logging.NOTSET: colorama.Fore.WHITE,
    }

    def formatMessage(self, record: logging.LogRecord):
        color = self.COLOURS[record.levelno]
        record.clevelname = f"{color}{record.levelname}{RESET_ALL}"
        record.clevelno = f"{color}{record.levelno}{RESET_ALL}"
        return super().formatMessage(record)


# For "English" variants =oP
ColorFormatter = ColourFormatter
