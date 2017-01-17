import mock
import pytest

from pyapp import checks
from pyapp.conf import settings
from pyapp.conf.helpers import plugins as conf_factory

from tests import factory


def factory_test(key):
    return "Factory[{}]".format(key)


class TestDefaultCache(object):
    def test_key_error_when_no_factory(self):
        target = conf_factory.DefaultCache()

        with pytest.raises(KeyError):
            target['foo']

        assert 'foo' not in target

    def test_factory_not_called_if_item_exists(self):
        target = conf_factory.DefaultCache(factory_test, foo='bar')

        actual = target['foo']
        assert actual == 'bar'
        assert 'foo' in target

    def test_factory_being_called_if_item_missing(self):
        target = conf_factory.DefaultCache(factory_test, foo='bar')

        actual = target['eek']
        assert actual == 'Factory[eek]'
        assert 'eek' in target
        assert target['eek'] == actual


class TestNamedFactory(object):
    def test_get_default(self):
        target = conf_factory.NamedPluginFactory('TEST_NAMED_FACTORY')

        actual = target()
        assert isinstance(actual, factory.Bar)
        assert str(actual) == 'Bar'
        assert actual.length == 42

    def test_get_specific(self):
        target = conf_factory.NamedPluginFactory('TEST_NAMED_FACTORY')

        actual = target('iron')
        assert isinstance(actual, factory.IronBar)
        assert str(actual) == 'Iron Bar'
        assert actual.length == 24

    def test_specify_alternate_default_name(self):
        target = conf_factory.NamedPluginFactory('TEST_NAMED_FACTORY', default_name='iron')

        actual = target()
        assert isinstance(actual, factory.IronBar)
        assert str(actual) == 'Iron Bar'
        assert actual.length == 24

    def test_unknown_instance_definition(self):
        target = conf_factory.NamedPluginFactory('TEST_NAMED_FACTORY')

        with pytest.raises(KeyError):
            target('copper')

    def test_with_abc_defined(self):
        target = conf_factory.NamedPluginFactory('TEST_NAMED_FACTORY', abc=factory.BarABC)

        actual = target()
        assert isinstance(actual, factory.Bar)

    def test_type_error_raised_if_not_correct_abc(self):
        target = conf_factory.NamedPluginFactory('TEST_NAMED_FACTORY', abc=factory.BarABC)

        with pytest.raises(TypeError):
            target('steel')

    def test_get_type_definition_is_cached(self, monkeypatch):
        mock_import = mock.Mock()
        mock_import.return_value = factory.Bar
        monkeypatch.setattr(conf_factory, '_import_type', mock_import)

        target = conf_factory.NamedPluginFactory('TEST_NAMED_FACTORY')

        actual1 = target()
        actual2 = target()

        assert isinstance(actual1, factory.Bar)
        assert isinstance(actual2, factory.Bar)
        assert actual1 is not actual2
        mock_import.assert_called_once_with('tests.factory.Bar')

    def test_available_definitions(self):
        target = conf_factory.NamedPluginFactory('TEST_NAMED_FACTORY')

        assert set(target.available) == {'default', 'iron', 'steel'}

    def test_checks_settings_missing(self):
        target = conf_factory.NamedPluginFactory('UNKNOWN_FACTORY_DEFINITION')

        actual = target.checks(settings=settings)

        assert isinstance(actual, checks.Critical)
        assert "INSTANCE DEFINITIONS MISSING" in actual.msg.upper()
        assert actual.obj == 'settings.UNKNOWN_FACTORY_DEFINITION'

    def test_checks_ignore_none_settings(self):
        with settings.modify() as patch:
            patch.FACTORY = None
            target = conf_factory.NamedPluginFactory('FACTORY')

            actual = target.checks(settings=settings)

        assert actual is None

    def test_checks_invalid_type(self):
        with settings.modify() as patch:
            patch.INVALID_SETTING = []

            target = conf_factory.NamedPluginFactory('INVALID_SETTING')
            actual = target.checks(settings=settings)

        assert isinstance(actual, checks.Critical)
        assert "NOT A DICT INSTANCE" in actual.msg.upper()
        assert actual.obj == 'settings.INVALID_SETTING'

    def test_checks_default_not_defined(self):
        with settings.modify() as patch:
            patch.FACTORY = {}

            target = conf_factory.NamedPluginFactory('FACTORY')
            actual = target.checks(settings=settings)

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

            target = conf_factory.NamedPluginFactory('FACTORY')
            actual = target.checks(settings=settings)

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

            target = conf_factory.NamedPluginFactory('FACTORY')
            actual = target.checks(settings=settings)

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

            target = conf_factory.NamedPluginFactory('FACTORY')
            actual = target.checks(settings=settings)

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

            target = conf_factory.NamedPluginFactory('FACTORY')
            actual = target.checks(settings=settings)

        assert len(actual) == 1
        message = actual[0]
        assert isinstance(message, checks.Error)
        assert "UNABLE TO IMPORT TYPE" in message.msg.upper()
        assert message.obj == 'settings.FACTORY[default]'


class TestNamedSingletonFactory(object):
    def test_get_default(self):
        target = conf_factory.NamedSingletonPluginFactory('TEST_NAMED_FACTORY')

        actual1 = target()
        actual2 = target()

        assert actual1 is actual2

    def test_get_type_definition_is_cached(self, monkeypatch):
        mock_import = mock.Mock()
        mock_import.return_value = factory.Bar
        monkeypatch.setattr(conf_factory, '_import_type', mock_import)

        target = conf_factory.NamedSingletonPluginFactory('TEST_NAMED_FACTORY')

        actual1 = target()
        actual2 = target()

        assert isinstance(actual1, factory.Bar)
        assert isinstance(actual2, factory.Bar)
        assert actual1 is actual2
        mock_import.assert_called_once_with('tests.factory.Bar')


class TestThreadLocalNamedSingletonPluginFactory(object):
    def test_get_default(self):
        target = conf_factory.ThreadLocalNamedSingletonPluginFactory('TEST_NAMED_FACTORY')

        actual1 = target()
        actual2 = target()

        assert actual1 is actual2

    def test_get_type_definition_is_cached(self, monkeypatch):
        mock_import = mock.Mock()
        mock_import.return_value = factory.Bar
        monkeypatch.setattr(conf_factory, '_import_type', mock_import)

        target = conf_factory.ThreadLocalNamedSingletonPluginFactory('TEST_NAMED_FACTORY')

        actual1 = target()
        actual2 = target()

        assert isinstance(actual1, factory.Bar)
        assert isinstance(actual2, factory.Bar)
        assert actual1 is actual2
        mock_import.assert_called_once_with('tests.factory.Bar')
