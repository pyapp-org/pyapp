import mock
import pytest
import tests.sample_app

from pyapp.app import arguments


class TestHandlerProxy:
    def test_basic_usage(self):
        def sample_handler(_):
            return 1

        mock_parser = mock.Mock()

        target = arguments.CommandProxy(sample_handler, mock_parser)

        assert sample_handler is target.handler
        assert sample_handler.__doc__ == target.__doc__
        assert sample_handler.__name__ == target.__name__
        assert sample_handler.__module__ == target.__module__
        assert target(None) == 1

    def test_with_arguments(self):
        @arguments.argument("--foo", dest="foo", help_text="Foo option")
        @arguments.argument("--bar", dest="bar", help_text="Bar option")
        def sample_handler():
            pass

        mock_parser = mock.Mock()
        arguments.CommandProxy(sample_handler, mock_parser)

        assert mock_parser.add_argument.call_count == 2
