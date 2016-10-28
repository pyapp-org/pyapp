import pytest

from pyapp.conf.loaders import module_loader
from pyapp.exceptions import InvalidConfiguration


class TestModuleLoader(object):
    def test__module_exists(self):
        target = module_loader.ModuleLoader('tests.settings')

        actual = dict(target)

        assert str(target) == 'python:tests.settings'
        assert actual == {
            'UPPER_VALUE': 'foo'
        }

    def test__module_not_found(self):
        target = module_loader.ModuleLoader('tests.unknown.settings')

        with pytest.raises(InvalidConfiguration):
            dict(target)

        assert str(target) == 'python:tests.unknown.settings'
