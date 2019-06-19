"""
Dependency Injection
~~~~~~~~~~~~~~~~~~~~

Support for dependency injection from factories.

"""

from typing import TypeVar, Generic, Callable, Sequence, Tuple

IT_co = TypeVar("IT_co", covariant=True)


class Inject(Generic[IT_co]):
    def __init__(self, *factory_args, **factory_kwargs):
        self.factory_args = factory_args
        self.factory_kwargs = factory_kwargs


class InjectionWrapper:
    def __init__(self, func: Callable, dependencies: Sequence[Tuple[str, Callable]]):
        self.func = func
        self.dependencies = dependencies

    def __call__(self, *args, **kwargs):
        for name, factory in self.dependencies:
            kwargs.setdefault(name, factory())
        return self.func(self, *args, **kwargs)


class Dependencies:
    def __init__(self, type_or_class: type):
        self.type_or_class = type_or_class
        self._dependencies()

    def __call__(self, *args, **kwargs):
        return self.type_or_class(*args, **kwargs)

    def _dependencies(self):
        functions = {
            n: f
            for n, f in self.type_or_class.__dict__.items()
            if isinstance(f, Callable)
        }

        for name, func in functions.items():
            dependencies = []
            for arg, annotation in func.__annotations__.items():
                if isinstance(annotation, Inject):
                    expected_type = annotation.__orig_class__.__args__[0]
                    dependencies.append((arg, lambda: "eek"))

            if dependencies:
                setattr(self.type_or_class, name, InjectionWrapper(func, dependencies))


@Dependencies
class MyObject:
    def __init__(self):
        self.arg = None

    def __str__(self):
        return str(self.arg)

    def call_me(self, arg: Inject[str]("default") = None):
        self.arg = arg


obj = MyObject()
obj.call_me()
print(obj)
