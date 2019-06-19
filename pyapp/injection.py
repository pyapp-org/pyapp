"""
Dependency Injection
~~~~~~~~~~~~~~~~~~~~

Support for dependency injection, from factories.

"""

from typing import TypeVar, Generic, Callable

IT_co = TypeVar("IT_co", covariant=True)


class Inject(Generic[IT_co]):
    def __init__(self, *factory_args, **factory_kwargs):
        self.factory_args = factory_args
        self.factory_kwargs = factory_kwargs


class InjectionWrapper:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass


class Dependencies:
    def __init__(self, type_or_class: type):
        self.type_or_class = type_or_class
        self._dependencies()

    def __call__(self, *args, **kwargs):
        return self.type_or_class(*args, **kwargs)

    def _dependencies(self):
        functions = {n: f for n, f in self.type_or_class.__dict__.items() if isinstance(f, Callable)}

        for name, func in functions.items():
            for arg, annotation in func.__annotations__.items():
                expected_type = annotation.__orig_class__.__args__[0]
                print(arg, expected_type)


@Dependencies
class MyObject:
    def __init__(self, arg: Inject[str]("default") = None):
        self.arg = arg

    def __str__(self):
        return str(self.arg)


obj = MyObject()
print(obj)
