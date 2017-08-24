import pytest

from pyapp import checks
from pyapp.conf import settings
from pyapp.conf.helpers import providers


class ProviderBaseTest(providers.ProviderBase):
    """
    Description.
    """
    name = "Test Provider"

    def __init__(self, foo):
        self.foo = foo


class ProviderFactoryTest(providers.ProviderFactoryBase):
    setting = "TEST_PROVIDERS"

    def __init__(self, ref=None, config=None):
        super(ProviderFactoryTest, self).__init__()
        self.ref = ref
        self.config = config or {}

    def load_config(self, *args, **kwargs):
        return self.ref, self.config


class TestProviderFactoryBase(object):
    def test_providers(self):
        target = ProviderFactoryTest()
        actual = target.providers

        assert len(actual) == 1

    def test_provider_summaries(self):
        target = ProviderFactoryTest()
        actual = target.provider_summaries

        assert len(actual) == 1
        assert actual == [
            providers.ProviderSummary(
                'tests.test_conf_helpers_providers.ProviderBaseTest', "Test Provider", "Description."
            )
        ]

    def test_get_provider(self):
        target = ProviderFactoryTest()
        actual = target.get_provider('tests.test_conf_helpers_providers.ProviderBaseTest')

        assert actual is ProviderBaseTest

    def test_get_provider__not_found(self):
        target = ProviderFactoryTest()

        with pytest.raises(providers.ProviderNotFound):
            target.get_provider('tests.wrong.ProviderBaseTest')

    def test_get_instance(self):
        target = ProviderFactoryTest('tests.test_conf_helpers_providers.ProviderBaseTest', {'foo': 'bar'})

        actual = target()

        assert isinstance(actual, ProviderBaseTest)
        assert actual.foo == 'bar'

    def test_get_instance__not_found(self):
        target = ProviderFactoryTest('tests.wrong.ProviderBaseTest')

        with pytest.raises(providers.ProviderNotFound):
            target()

    @pytest.mark.parametrize('provider_settings, expected', (
        (None, None),
        ([], []),
        ({}, checks.Critical(
            u"Provider definitions defined in settings not a list/tuple instance.",
            u"Change setting TEST_PROVIDERS to be a list or tuple in settings file.",
            u"settings.TEST_PROVIDERS"
        )),
        (['tests.test_conf_helpers_providers.ProviderBaseTest'], []),
        ([123], [checks.Critical(
            u"Provider definition is not a string.",
            u"Change definition to be a string in settings.",
            u"settings.TEST_PROVIDERS[0]"
        )])
    ))
    def test_checks(self, provider_settings, expected):
        target = ProviderFactoryTest()

        with settings.modify() as ctx:
            ctx.TEST_PROVIDERS = provider_settings

            actual = target.checks(settings=settings)

            assert actual == expected

    def test_checks__missing_settings(self):
        target = ProviderFactoryTest()

        with settings.modify() as ctx:
            del ctx.TEST_PROVIDERS

            actual = target.checks(settings=settings)

            assert actual == checks.Critical(
                u"Provider definitions missing from settings.",
                u"Add a TEST_PROVIDERS entry into settings.",
                u"settings.TEST_PROVIDERS"
            )

    def test_checks__invalid_import(self):
        target = ProviderFactoryTest()

        with settings.modify() as ctx:
            ctx.TEST_PROVIDERS = ['tests.test_conf_helpers_providers.ProviderBaseTest', 'tests.wrong.ProviderBaseTest']

            actual = target.checks(settings=settings)[0]

            assert isinstance(actual, checks.Critical)
            assert actual.msg == u"Unable to import provider type."
            assert actual.obj == u"settings.TEST_PROVIDERS[1]"
