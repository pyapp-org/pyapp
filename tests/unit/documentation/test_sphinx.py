from pyapp.documentation import sphinx


class TestSettingsDocumenter:
    def test_can_document_member(self):
        actual = sphinx.SettingsDocumenter.can_document_member(None, "foo", False, None)

        assert actual is False
