import mock
import pytest

import pyapp.factory

from pyapp import checks
from pyapp.conf import settings
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

    def test_available_definitions(self):
        target = pyapp.factory.NamedFactory('TEST_NAMED_FACTORY')

        assert set(target.available) == {'default', 'iron', 'steel'}

    def test_checks_settings_missing(self):
        target = pyapp.factory.NamedFactory('UNKNOWN_FACTORY_DEFINITION')

        actual = target.checks(settings)

        assert isinstance(actual, checks.Critical)
        assert "INSTANCE DEFINITIONS MISSING" in actual.msg.upper()
        assert actual.obj == 'settings.UNKNOWN_FACTORY_DEFINITION'

    def test_checks_ignore_none_settings(self):
        with settings.modify() as patch:
            patch.FACTORY = None
            target = pyapp.factory.NamedFactory('FACTORY')

            actual = target.checks(settings)

        assert actual is None

    def test_checks_invalid_type(self):
        with settings.modify() as patch:
            patch.INVALID_SETTING = []

            target = pyapp.factory.NamedFactory('INVALID_SETTING')
            actual = target.checks(settings)

        assert isinstance(actual, checks.Critical)
        assert "NOT A DICT INSTANCE" in actual.msg.upper()
        assert actual.obj == 'settings.INVALID_SETTING'

    def test_checks_un_defined_value(self):
        with settings.modify() as patch:
            patch.INVALID_SETTING = []

            target = pyapp.factory.NamedFactory('INVALID_SETTING')
            actual = target.checks(settings)

        assert isinstance(actual, checks.Critical)
        assert "NOT A DICT INSTANCE" in actual.msg.upper()
        assert actual.obj == 'settings.INVALID_SETTING'

    def test_checks_default_not_defined(self):
        with settings.modify() as patch:
            patch.FACTORY = {}

            target = pyapp.factory.NamedFactory('FACTORY')
            actual = target.checks(settings)

        assert len(actual) == 1
        message = actual[0]
        assert isinstance(message, checks.Warn)
        assert "DEFAULT DEFINITION NOT DEFINED" in message.msg.upper()
        assert message.obj == 'settings.FACTORY'

    def test_checks_invalid_instance_def_type(self):
        with settings.modify() as patch:
            patch.FACTORY = {
                'default': {}
            }

            target = pyapp.factory.NamedFactory('FACTORY')
            actual = target.checks(settings)

        assert len(actual) == 1
        message = actual[0]
        assert isinstance(message, checks.Critical)
        assert "DEFINITION IS NOT A LIST/TUPLE" in message.msg.upper()
        assert message.obj == 'settings.FACTORY[default]'

    def test_checks_invalid_instance_def_length(self):
        with settings.modify() as patch:
            patch.FACTORY = {
                'default': ('a', 'b', 'c')
            }

            target = pyapp.factory.NamedFactory('FACTORY')
            actual = target.checks(settings)

        assert len(actual) == 1
        message = actual[0]
        assert isinstance(message, checks.Critical)
        assert "NOT A TYPE NAME, KWARG" in message.msg.upper()
        assert message.obj == 'settings.FACTORY[default]'

    def test_checks_invalid_instance_def_kwargs(self):
        with settings.modify() as patch:
            patch.FACTORY = {
                'default': ('tests.factory.IronBar', [])
            }

            target = pyapp.factory.NamedFactory('FACTORY')
            actual = target.checks(settings)

        assert len(actual) == 1
        message = actual[0]
        assert isinstance(message, checks.Critical)
        assert "KWARGS IS NOT A DICT" in message.msg.upper()
        assert message.obj == 'settings.FACTORY[default]'

    def test_checks_invalid_instance_def_cannot_import(self):
        with settings.modify() as patch:
            patch.FACTORY = {
                'default': ('a.b.c', {})
            }

            target = pyapp.factory.NamedFactory('FACTORY')
            actual = target.checks(settings)

        assert len(actual) == 1
        message = actual[0]
        assert isinstance(message, checks.Error)
        assert "UNABLE TO IMPORT TYPE" in message.msg.upper()
        assert message.obj == 'settings.FACTORY[default]'


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


class TestThreadLocalNamedSingletonFactory(object):
    def test_get_default(self):
        target = pyapp.factory.ThreadLocalNamedSingletonFactory('TEST_NAMED_FACTORY')

        actual1 = target()
        actual2 = target()

        assert actual1 is actual2

    def test_get_type_definition_is_cached(self, monkeypatch):
        mock_import = mock.Mock()
        mock_import.return_value = factory.Bar
        monkeypatch.setattr(pyapp.factory, '_import_type', mock_import)

        target = pyapp.factory.ThreadLocalNamedSingletonFactory('TEST_NAMED_FACTORY')

        actual1 = target()
        actual2 = target()

        assert isinstance(actual1, factory.Bar)
        assert isinstance(actual2, factory.Bar)
        assert actual1 is actual2
        mock_import.assert_called_once_with('tests.factory.Bar')
