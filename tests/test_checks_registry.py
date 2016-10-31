import pytest

from pyapp.checks import registry


class TestCheckRegistry(object):
    def test_register__with_decorator_without_tags(self):
        target = registry.CheckRegistry()

        @target.register
        def my_check_func(**kwargs):
            pass

        assert len(target.registered_checks) == 1
        assert my_check_func in target.registered_checks
        assert len(my_check_func.tags) == 0

    def test_register__with_decorator_with_tags(self):
        target = registry.CheckRegistry()

        @target.register("foo", "bar")
        def my_check_func(**kwargs):
            pass

        assert len(target.registered_checks) == 1
        assert my_check_func in target.registered_checks
        assert len(my_check_func.tags) == 2

    def test_register__with_method(self):
        target = registry.CheckRegistry()

        def my_check_func(**kwargs):
            pass

        target.register(my_check_func, "foo", "bar")

        assert len(target.registered_checks) == 1
        assert my_check_func in target.registered_checks
        assert len(my_check_func.tags) == 2
