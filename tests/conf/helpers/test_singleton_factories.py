from pyapp.conf import helpers


class ExampleNamedSingletonFactory(helpers.NamedSingletonFactory):
    def create(self, name: str = None):
        return object()


class TestNamedSingletonFactory:
    def test_create__same_name_same_instance(self):
        target = ExampleNamedSingletonFactory("FOO")

        actual_a = target.create()
        actual_b = target.create()

        assert actual_a is actual_b

    def test_create__different_name_different_instance(self):
        target = ExampleNamedSingletonFactory("FOO")

        actual_a = target.create("A")
        actual_b = target.create("B")

        assert actual_a is not actual_b


class ExampleThreadLocalNamedSingletonFactory(helpers.ThreadLocalNamedSingletonFactory):
    def create(self, name: str = None):
        return object()


class TestThreadLocalNamedSingletonFactory:
    """
    Note this test is only within a single thead
    """

    def test_create__same_name_same_instance(self):
        target = ExampleThreadLocalNamedSingletonFactory("FOO")

        actual_a = target.create()
        actual_b = target.create()

        assert actual_a is actual_b

    def test_create__different_name_different_instance(self):
        target = ExampleThreadLocalNamedSingletonFactory("FOO")

        actual_a = target.create("A")
        actual_b = target.create("B")

        assert actual_a is not actual_b
