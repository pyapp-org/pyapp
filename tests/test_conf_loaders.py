import pytest

from pyapp.conf import loaders
from pyapp.exceptions import InvalidConfiguration


class TestModuleLoader(object):
    def test__module_exists(self):
        target = loaders.ModuleLoader('tests.settings')

        actual = dict(target)

        assert str(target) == 'python:tests.settings'
        assert actual == {
            'UPPER_VALUE': 'foo'
        }

    def test__module_not_found(self):
        target = loaders.ModuleLoader('tests.unknown.settings')

        with pytest.raises(InvalidConfiguration):
            dict(target)

        assert str(target) == 'python:tests.unknown.settings'


class TestFactory(object):
    @pytest.mark.parametrize(('settings_uri', 'expected', 'str_value'), (
        ('sample.settings', loaders.ModuleLoader, 'python:sample.settings'),
        ('python:sample.settings', loaders.ModuleLoader, 'python:sample.settings'),
        ('file:///path/to/sample.json', loaders.FileLoader, 'file:///path/to/sample.json'),
    ))
    def test__loaders_correctly_resolved(self, settings_uri, expected, str_value):
        actual = loaders.factory(settings_uri)

        assert isinstance(actual, expected)
        assert str(actual) == str_value

    @pytest.mark.parametrize(('settings_uri', 'expected'), (
        ('py:sample.settings', 'Unknown scheme `py` in settings URI:'),
    ))
    def test__invalid_settings_uri(self, settings_uri, expected):
        with pytest.raises(InvalidConfiguration) as e:
            loaders.factory(settings_uri)

        assert str(e.value).startswith(expected)
