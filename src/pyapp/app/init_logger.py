"""Logger used in the initial setup."""

import logging
from typing import List


class InitHandler(logging.Handler):
    """Handler that provides initial logging and captures logging up to a certain
    level, it is then replayed once logging has been initialised.
    """

    def __init__(self, handler: logging.Handler, pass_through_level=logging.WARNING):
        super().__init__(logging.DEBUG)
        self.handler = handler
        self.pass_through_level = pass_through_level
        self._store: List[logging.LogRecord] = []

    def handle(self, record: logging.LogRecord) -> None:
        """Handle record"""
        self._store.append(record)
        if record.levelno >= self.pass_through_level:
            super().handle(record)

    def replay(self):
        """Replay stored log records"""

        for record in self._store:
            logger = logging.getLogger(record.name)
            if logger.isEnabledFor(record.levelno):
                logger.handle(record)
        self._store.clear()

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the record"""

        # Pass to initial handler
        self.handler.emit(record)
