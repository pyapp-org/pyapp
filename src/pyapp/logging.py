"""
Logger used in the initial setup.
"""
import logging
from typing import List

import colorama


class InitHandler(logging.Handler):
    """
    Handler that provides initial logging and captures logging up to a certain
    level, it is then replayed once logging has been initialised.
    """

    def __init__(self, handler: logging.Handler, pass_through_level=logging.WARNING):
        super().__init__(logging.DEBUG)
        self.handler = handler
        self.pass_through_level = pass_through_level
        self._store: List[logging.LogRecord] = []

    def handle(self, record: logging.LogRecord) -> None:
        """
        Handle record
        """
        self._store.append(record)
        if record.levelno >= self.pass_through_level:
            super().handle(record)

    def replay(self):
        """
        Replay stored log records
        """

        for record in self._store:
            logging.getLogger(record.name).handle(record)
        self._store.clear()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit the record
        """

        # Pass to initial handler
        self.handler.emit(record)


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
