import pytest

from pyapp.conf import loaders
from pyapp.exceptions import InvalidConfiguration


class TestModuleLoader(object):
    def test__module_exists(self):
        target = loaders.ModuleLoader('tests.settings')

        actual = dict(target)

        assert str(target) == 'python:tests.settings'
        assert all(key.isupper() for key in actual)

    def test__module_not_found(self):
        target = loaders.ModuleLoader('tests.unknown.settings')

        with pytest.raises(InvalidConfiguration):
            dict(target)

        assert str(target) == 'python:tests.unknown.settings'


class TestSettingsLoaderRegistry(object):
    def test_register__as_decorator(self):
        target = loaders.SettingsLoaderRegistry()

        @target.register
        class SimpleSettings(object):
            scheme = 'eek'

            @classmethod
            def from_url(cls, settings_url):
                return cls(settings_url)

            def __init__(self, settings_url):
                self.settings_url = settings_url

            def __iter__(self):
                return {
                    'SIMPLE': self.settings_url
                }.items()

        assert 'eek' in target.loaders
        assert isinstance(target.factory('eek:sample'), SimpleSettings)

    def test_register__as_method(self):
        target = loaders.SettingsLoaderRegistry()

        class SimpleSettings(object):
            @classmethod
            def from_url(cls, settings_url):
                return cls(settings_url)

            def __init__(self, settings_url):
                self.settings_url = settings_url

            def __iter__(self):
                return {
                    'SIMPLE': self.settings_url
                }.items()

        target.register(SimpleSettings, scheme='eek')

        assert 'eek' in target.loaders
        assert isinstance(target.factory('eek:sample'), SimpleSettings)

    @pytest.mark.parametrize(('settings_uri', 'expected', 'str_value'), (
        ('sample.settings', loaders.ModuleLoader, 'python:sample.settings'),
        ('python:sample.settings', loaders.ModuleLoader, 'python:sample.settings'),
        ('file:///path/to/sample.json', loaders.FileLoader, 'file:///path/to/sample.json'),
    ))
    def test_factory__loaders_correctly_resolved(self, settings_uri, expected, str_value):
        target = loaders.SettingsLoaderRegistry()

        actual = target.factory(settings_uri)

        assert isinstance(actual, expected)
        assert str(actual) == str_value

    @pytest.mark.parametrize(('settings_uri', 'expected'), (
        ('py:sample.settings', 'Unknown scheme `py` in settings URI:'),
    ))
    def test_factory__invalid_settings_uri(self, settings_uri, expected):
        target = loaders.SettingsLoaderRegistry()

        with pytest.raises(InvalidConfiguration) as e:
            target.factory(settings_uri)

        assert str(e.value).startswith(expected)
