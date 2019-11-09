import logging

from colorama import Fore, Back, Style

RESET_ALL = Style.RESET_ALL


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
        logging.CRITICAL: Fore.WHITE + Back.RED,
        logging.ERROR: Fore.RED + Style.BRIGHT,
        logging.WARNING: Fore.YELLOW + Style.BRIGHT,
        logging.INFO: Fore.CYAN + Style.BRIGHT,
        logging.DEBUG: Fore.MAGENTA + Style.BRIGHT,
        logging.NOTSET: Fore.LIGHTBLACK_EX,
    }

    def formatMessage(self, record: logging.LogRecord):
        color = self.COLOURS[record.levelno]
        record.clevelname = f"{color}{record.levelname}{RESET_ALL}"
        record.clevelno = f"{color}{record.levelno}{RESET_ALL}"
        return super().formatMessage(record)


# For "English" variants =oP
ColorFormatter = ColourFormatter
