import mock
import pytest
import tests.sample_app

from pyapp.app import HandlerProxy, add_argument, CliApplication


class TestHandlerProxy(object):
    def test_basic_usage(self):
        def sample_handler():
            return "Success"

        mock_parser = mock.Mock()

        target = HandlerProxy(sample_handler, mock_parser)

        assert sample_handler is target.handler
        assert mock_parser is target.sub_parser
        assert sample_handler.__doc__ == target.__doc__
        assert sample_handler.__name__ == target.__name__
        assert sample_handler.__module__ == target.__module__
        assert target() == 'Success'

    def test_with_arguments(self):

        @add_argument('--foo', dest='foo', help='Foo option')
        @add_argument('--bar', dest='bar', help='Bar option')
        def sample_handler():
            pass

        mock_parser = mock.Mock()
        HandlerProxy(sample_handler, mock_parser)

        assert mock_parser.add_argument.call_count == 2


class TestCliApplication(object):
    def test_initialisation(self):
        target = CliApplication(tests.sample_app)

        assert target.root_module is tests.sample_app
        assert target.application_settings == 'tests.sample_app.default_settings'
        assert len(target._handlers) == 2

    def test_initialisation_alternate_settings(self):
        target = CliApplication(
            tests.sample_app,
            application_settings='tests.runtime_settings'
        )

        assert target.application_settings == 'tests.runtime_settings'

    def test_dispatch(self):
        closure = {}

        target = CliApplication(tests.sample_app)

        @target.register_handler(cli_name='sample')
        @add_argument('--foo', dest='foo')
        def sample_handler(opts):
            closure['opts'] = opts

        target.dispatch(args=('sample', '--foo', 'bar'))

        assert closure['opts'].foo == 'bar'
