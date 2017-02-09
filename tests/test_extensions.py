from pyapp.extensions.registry import ExtensionRegistry


class TestExtensionRegistry(object):
    def test_load_with_metadata(self):
        target = ExtensionRegistry()

        target.load('tests.sample_ext')

        assert target.summary() == [{
            'name': 'Sample Extension',
            'version': '3.2.1',
            'package': 'tests.sample_ext',
            'checks': 'tests.sample_ext.checks',
            'default_settings': 'tests.sample_ext.default_settings',
        }]

    def test_load_without_metadata(self):
        target = ExtensionRegistry()

        target.load('tests.sample_ext_simple')

        assert target.summary() == [{
            'name': 'tests.sample_ext_simple',
            'version': None,
            'package': 'tests.sample_ext_simple',
            'checks': None,
            'default_settings': None,
        }]

    def test_load_from_settings(self):
        target = ExtensionRegistry()

        target.load_from_settings()

        assert target.summary() == [{
            'name': 'Sample Extension',
            'version': '3.2.1',
            'package': 'tests.sample_ext',
            'checks': 'tests.sample_ext.checks',
            'default_settings': 'tests.sample_ext.default_settings',
        }, {
            'name': 'tests.sample_ext_simple',
            'version': None,
            'package': 'tests.sample_ext_simple',
            'checks': None,
            'default_settings': None,
        }]

    def test_trigger_ready(self):
        import tests.sample_ext

        tests.sample_ext.set_ready = False

        target = ExtensionRegistry()
        target.load('tests.sample_ext')

        target.trigger_ready()

        assert tests.sample_ext.set_ready is True
