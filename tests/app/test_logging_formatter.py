import logging

import colorama
import pytest

from pyapp.app import logging_formatter


@pytest.mark.parametrize(
    "level",
    (
        logging.CRITICAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
        logging.NOTSET,
    ),
)
def test_format_message(level):
    record = logging.LogRecord("test", level, "foo", 42, "bar", (), False)
    target = logging_formatter.ColourFormatter("%(clevelno)s - %(clevelname)s")

    actual = target.formatMessage(record)

    assert actual.endswith(colorama.Style.RESET_ALL)
