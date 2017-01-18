import pytest

from pyapp import checks
from pyapp.conf import settings
from pyapp.conf import helpers


class TestNamedConfiguration(object):
    def test_get_default(self):
        target = helpers.NamedConfiguration('TEST_NAMED_CONFIG')

        actual = target.get()
        assert actual == {'length': 42, 'foo': 'bar'}

    def test_get_specific(self):
        target = helpers.NamedConfiguration('TEST_NAMED_CONFIG')

        actual = target.get('eek')
        assert actual == {'length': 24, 'foo': 'bar'}

    def test_specify_alternate_default_name(self):
        target = helpers.NamedConfiguration('TEST_NAMED_CONFIG', default_name='eek')

        actual = target.get('eek')
        assert actual == {'length': 24, 'foo': 'bar'}

    def test_unknown_instance_definition(self):
        target = helpers.NamedConfiguration('TEST_NAMED_CONFIG')

        with pytest.raises(KeyError):
            target.get('other')

    def test_defaults_are_applied(self):
        target = helpers.NamedConfiguration(
            'TEST_NAMED_CONFIG',
            defaults={
                'bar': 123
            },
            required_keys=('length',),
            optional_keys=('foo',)
        )

        actual = target.get()
        assert actual == {'length': 42, 'foo': 'bar', 'bar': 123}

    def test_checks_settings_missing(self):
        target = helpers.NamedConfiguration('UNKNOWN_NAMED_CONFIG')

        actual = target.checks(settings=settings)

        assert isinstance(actual, checks.Critical)
        assert "CONFIG DEFINITIONS MISSING" in actual.msg.upper()
        assert actual.obj == 'settings.UNKNOWN_NAMED_CONFIG'

    def test_checks_ignore_none_settings(self):
        with settings.modify() as patch:
            patch.NAMED_CONFIG = None
            target = helpers.NamedConfiguration('NAMED_CONFIG')

            actual = target.checks(settings=settings)

        assert actual is None
        assert actual is None

    def test_checks_invalid_type(self):
        with settings.modify() as patch:
            patch.NAMED_CONFIG = []

            target = helpers.NamedConfiguration('NAMED_CONFIG')
            actual = target.checks(settings=settings)

        assert isinstance(actual, checks.Critical)
        assert "NOT A DICT INSTANCE" in actual.msg.upper()
        assert actual.obj == 'settings.NAMED_CONFIG'

    def test_checks_default_not_defined(self):
        with settings.modify() as patch:
            patch.NAMED_CONFIG = {}

            target = helpers.NamedConfiguration('NAMED_CONFIG')
            actual = target.checks(settings=settings)

        assert len(actual) == 1
        message = actual[0]
        assert isinstance(message, checks.Warn)
        assert "DEFAULT DEFINITION NOT DEFINED" in message.msg.upper()
        assert message.obj == 'settings.NAMED_CONFIG'

    def test_checks_invalid_instance_def_type(self):
        with settings.modify() as patch:
            patch.NAMED_CONFIG = {
                'default': []
            }

            target = helpers.NamedConfiguration('NAMED_CONFIG')
            actual = target.checks(settings=settings)

        assert len(actual) == 1
        message = actual[0]
        assert isinstance(message, checks.Critical)
        assert "DEFINITION ENTRY IS NOT A DICT" in message.msg.upper()
        assert message.obj == 'settings.NAMED_CONFIG[default]'

    def test_checks_required_key_missing(self):
        with settings.modify() as patch:
            patch.NAMED_CONFIG = {
                'default': {}
            }

            target = helpers.NamedConfiguration(
                'NAMED_CONFIG',
                required_keys=('foo',)
            )
            actual = target.checks(settings=settings)

        assert len(actual) == 1
        message = actual[0]
        assert isinstance(message, checks.Critical)
        assert "DOES NOT CONTAIN `FOO` VALUE" in message.msg.upper()
        assert message.obj == 'settings.NAMED_CONFIG[default]'

    def test_checks_unknown_key(self):
        with settings.modify() as patch:
            patch.NAMED_CONFIG = {
                'default': {
                    'foo': 123,
                    'eek': 321
                }
            }

            target = helpers.NamedConfiguration(
                'NAMED_CONFIG',
                required_keys=('foo',),
                optional_keys=('bar',)
            )
            actual = target.checks(settings=settings)

        assert len(actual) == 1
        message = actual[0]
        assert isinstance(message, checks.Warn)
        assert "CONTAINS UNKNOWN VALUE `EEK`" in message.msg.upper()
        assert message.obj == 'settings.NAMED_CONFIG[default][eek]'

    def test_checks_ignore_unknown_keys(self):
        with settings.modify() as patch:
            patch.NAMED_CONFIG = {
                'default': {
                    'foo': 123,
                    'eek': 321
                }
            }

            target = helpers.NamedConfiguration('NAMED_CONFIG')
            actual = target.checks(settings=settings)

        assert len(actual) == 0
