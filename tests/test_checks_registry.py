from pyapp.checks import registry
from pyapp.checks import messages


class TestCheckRegistry(object):
    def test_register__with_decorator_without_tags(self):
        target = registry.CheckRegistry()

        @target.register
        def my_check_func(**kwargs):
            pass

        assert len(target.registered_checks) == 1
        assert my_check_func in target.registered_checks
        assert len(my_check_func._check__tags) == 0

    def test_register__with_decorator_with_tags(self):
        target = registry.CheckRegistry()

        @target.register("foo", "bar")
        def my_check_func(**kwargs):
            pass

        assert len(target.registered_checks) == 1
        assert my_check_func in target.registered_checks
        assert len(my_check_func._check__tags) == 2

    def test_register__with_method(self):
        target = registry.CheckRegistry()

        def my_check_func(**kwargs):
            pass

        target.register(my_check_func, "foo", "bar")

        assert len(target.registered_checks) == 1
        assert my_check_func in target.registered_checks
        assert len(my_check_func._check__tags) == 2

    def test_register__same_check(self):
        target = registry.CheckRegistry()

        @target.register
        def my_check_func(**kwargs):
            pass

        target.register(my_check_func, "foo", "bar")

        assert len(target.registered_checks) == 1
        assert my_check_func in target.registered_checks
        assert len(my_check_func._check__tags) == 2

    def test_register__attached_check(self):
        target = registry.CheckRegistry()

        def my_func():
            return 'foo'

        def my_func_checks(**kwargs):
            pass
        my_func.checks = my_func_checks

        target.register(my_func, 'foo')

        assert len(target.registered_checks) == 1
        assert my_func in target.registered_checks
        assert len(my_func._check__tags) == 1

    def test_run_checks__all_successful(self):
        target = registry.CheckRegistry()

        @target.register
        def check_1(settings, **kwargs):
            assert settings

        @target.register()
        def check_2(settings, **kwargs):
            assert settings

        actual = target.run_checks()

        assert len(actual) == 0

    def test_run_checks__singular_and_multiple_responses(self):
        target = registry.CheckRegistry()

        @target.register
        def check_1(settings, **kwargs):
            return messages.Info("Message1")

        @target.register()
        def check_2(settings, **kwargs):
            return messages.Info("Message2"), messages.Info("Message3")

        actual = target.run_checks()

        assert len(actual) == 3
        assert [
            messages.Info("Message1"),
            messages.Info("Message2"),
            messages.Info("Message3"),
        ] == actual

    def test_run_checks__filter_by_tag(self):
        target = registry.CheckRegistry()

        @target.register('foo')
        def check_1(settings, **kwargs):
            return messages.Info("Message1")

        @target.register('foo', 'bar')
        def check_2(settings, **kwargs):
            return messages.Info("Message2")

        @target.register('bar')
        def check_3(settings, **kwargs):
            return messages.Info("Message3"), messages.Info("Message4")

        actual = target.run_checks(['foo'])
        assert [
            messages.Info("Message1"),
            messages.Info("Message2"),
        ] == actual

        actual = target.run_checks(['bar'])
        assert [
            messages.Info("Message2"),
            messages.Info("Message3"),
            messages.Info("Message4"),
        ] == actual

        actual = target.run_checks(['foo', 'bar'])
        assert [
            messages.Info("Message1"),
            messages.Info("Message2"),
            messages.Info("Message3"),
            messages.Info("Message4"),
        ] == actual

    def test_run_checks__attached_checks(self):
        target = registry.CheckRegistry()

        class MyClass(object):
            def checks(self, settings, **kwargs):
                return messages.Info("Message1"), messages.Info("Message2")
        instance = MyClass()

        target.register(instance)

        actual = target.run_checks()
        assert [
            messages.Info("Message1"),
            messages.Info("Message2"),
        ] == actual
