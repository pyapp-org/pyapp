import colorama
import logging


class ColourFormatter(logging.Formatter):
    """
    Formatter that adds colourised versions of log levels
    """
    level_colours = {
        logging.CRITICAL: colorama.Fore.RED + colorama.Style.BRIGHT,
        logging.ERROR: colorama.Fore.RED,
        logging.WARNING: colorama.Fore.BLUE,
        logging.INFO: colorama.Fore.GREEN,
        logging.DEBUG: colorama.Fore.LIGHTBLACK_EX,
        logging.NOTSET: colorama.Fore.WHITE,
    }

    def formatMessage(self, record: logging.LogRecord):
        color = self.level_colours[record.levelno]
        record.clevelname = f"{color}{record.levelname}{colorama.Style.RESET_ALL}"
        return super().formatMessage(record)


# For "English" variants =oP
ColorFormatter = ColourFormatter
