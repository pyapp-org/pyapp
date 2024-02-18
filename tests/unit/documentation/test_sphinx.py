from unittest.mock import Mock

import pytest
from pyapp.documentation import sphinx


class TestSettingsDocumenter:
    @pytest.fixture
    def documenter(self):
        return sphinx.SettingsDocumenter(None, None, None)

    def test_can_document_member(self):
        actual = sphinx.SettingsDocumenter.can_document_member(None, "foo", False, None)

        assert actual is False

    def test_add_block(self):
        target = sphinx.SettingsDocumenter(None, None, None)
        target.add_line = Mock(sphinx.SettingsDocumenter.add_line)

        target.add_block("Line 1\nLine 2\n")

        assert target.result == ["Line 1", "Line 2", ""]
