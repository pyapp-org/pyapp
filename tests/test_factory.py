import pytest

import pyapp.factory
from pyapp.conf import settings


def factory_test(key):
    return "Factory[{}]".format(key)


class TestDefaultCache(object):
    def test_key_error_when_no_factory(self):
        target = pyapp.factory.DefaultCache()

        with pytest.raises(KeyError):
            actual = target['foo']

        assert 'foo' not in target

    def test_factory_not_called_if_item_exists(self):
        target = pyapp.factory.DefaultCache(factory_test, foo='bar')

        actual = target['foo']
        assert actual == 'bar'
        assert 'foo' in target

    def test_factory_being_called_if_item_missing(self):
        target = pyapp.factory.DefaultCache(factory_test, foo='bar')

        actual = target['eek']
        assert actual == 'Factory[eek]'
        assert 'eek' in target
        assert target['eek'] == actual


class TestNamedFactory(object):
    def test_settings_not_defined(self):
        with pytest.raises(ValueError):
            pyapp.factory.NamedFactory('UNKNOWN_NAMED_FACTORY')

    def test_get_default(self):
        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY')

        actual = target()
        assert str(actual) == 'Bar'
        assert actual.length == 42

    def test_get_specific(self):
        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY')

        actual = target('iron')
        assert str(actual) == 'Iron Bar'
        assert actual.length == 24

    def test_specify_alternate_default_name(self):
        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY', default_name='iron')

        actual = target()
        assert str(actual) == 'Iron Bar'
        assert actual.length == 24

    def test_unknown_instance_definition(self):
        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY')

        with pytest.raises(KeyError):
            target('steel')

