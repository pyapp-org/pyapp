import pyapp.conf


class TestSettings(object):
    def test_configure(self):
        settings = pyapp.conf.Settings()
        settings.configure('tests.settings')

        assert 'python:tests.settings' in settings.SETTINGS_SOURCES
        assert hasattr(settings, 'UPPER_VALUE')
        assert not hasattr(settings, 'lower_value')
        assert not hasattr(settings, 'mixed_VALUE')

    def test_configure__from_environment(self, monkeypatch):
        monkeypatch.setenv('PYAPP_SETTINGS', 'tests.runtime_settings')

        settings = pyapp.conf.Settings()
        settings.configure('tests.settings')

        assert 'python:tests.runtime_settings' in settings.SETTINGS_SOURCES
        assert hasattr(settings, 'UPPER_VALUE')
        assert hasattr(settings, 'RUNTIME_VALUE')
        assert not hasattr(settings, 'lower_value')
        assert not hasattr(settings, 'mixed_VALUE')
