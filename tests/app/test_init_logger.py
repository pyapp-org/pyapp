import logging
from unittest.mock import Mock

from pyapp.app import init_logger


class TestInitHandler:
    def test_over_threshold(self):
        """
        Given a record that has a log level over the threshold is passed to default handler
        """
        mock_handler = Mock()
        target = init_logger.InitHandler(mock_handler)
        record = logging.LogRecord(
            "Foo", logging.ERROR, "path.to.module", 42, "Bar", {}, None
        )

        target.handle(record)

        mock_handler.emit.assert_called_with(record)
