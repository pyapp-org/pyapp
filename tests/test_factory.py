import mock
import pytest

import pyapp.factory
from tests import factory


def factory_test(key):
    return "Factory[{}]".format(key)


class TestDefaultCache(object):
    def test_key_error_when_no_factory(self):
        target = pyapp.factory.DefaultCache()

        with pytest.raises(KeyError):
            target['foo']

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
        assert isinstance(actual, factory.Bar)
        assert str(actual) == 'Bar'
        assert actual.length == 42

    def test_get_specific(self):
        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY')

        actual = target('iron')
        assert isinstance(actual, factory.IronBar)
        assert str(actual) == 'Iron Bar'
        assert actual.length == 24

    def test_specify_alternate_default_name(self):
        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY', default_name='iron')

        actual = target()
        assert isinstance(actual, factory.IronBar)
        assert str(actual) == 'Iron Bar'
        assert actual.length == 24

    def test_unknown_instance_definition(self):
        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY')

        with pytest.raises(KeyError):
            target('copper')

    def test_with_abc_defined(self):
        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY', abc=factory.BarABC)

        actual = target()
        assert isinstance(actual, factory.Bar)

    def test_type_error_raised_if_not_correct_abc(self):
        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY', abc=factory.BarABC)

        with pytest.raises(TypeError):
            target('steel')

    def test_get_type_definition_is_cached(self, monkeypatch):
        mock_import = mock.Mock()
        mock_import.return_value = factory.Bar
        monkeypatch.setattr(pyapp.factory, '_import_type', mock_import)

        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY')

        actual1 = target()
        actual2 = target()

        assert isinstance(actual1, factory.Bar)
        assert isinstance(actual2, factory.Bar)
        assert actual1 is not actual2
        mock_import.assert_called_once_with('tests.factory.Bar')


class TestNamedSingletonFactory(object):
    def test_get_default(self):
        target = pyapp.factory.NamedSingletonFactory('TEST_NAMED_FACTORY')

        actual1 = target()
        actual2 = target()

        assert actual1 is actual2

    def test_get_type_definition_is_cached(self, monkeypatch):
        mock_import = mock.Mock()
        mock_import.return_value = factory.Bar
        monkeypatch.setattr(pyapp.factory, '_import_type', mock_import)

        target = pyapp.factory.NamedSingletonFactory('TEST_NAMED_FACTORY')

        actual1 = target()
        actual2 = target()

        assert isinstance(actual1, factory.Bar)
        assert isinstance(actual2, factory.Bar)
        assert actual1 is actual2
        mock_import.assert_called_once_with('tests.factory.Bar')
