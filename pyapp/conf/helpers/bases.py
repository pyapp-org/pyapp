from __future__ import unicode_literals

import threading


class DefaultCache(dict):
    """
    Very similar to :py:class:`collections.defaultdict` (using __missing__)
    however passes the specified key to the default factory method.
    """
    def __init__(self, default_factory=None, **kwargs):
        super(DefaultCache, self).__init__(**kwargs)
        self.default_factory = default_factory

    def __missing__(self, key):
        if not self.default_factory:
            raise KeyError(key)
        self[key] = value = self.default_factory(key)
        return value


class FactoryMixin(object):
    def __call__(self, name=None):
        """
        Get a named instance.

        :param name: Named configuration; default is to the name specified by
            the `default_name` property.
        :returns: New instanced of the named type.

        """
        return self.create_instance(name)

    def create_instance(self, name=None):
        raise NotImplementedError()


class SingletonFactoryMixin(FactoryMixin):
    """"
    Mixin that provides a single named instance.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents.

    If your instance types are not thread safe it is recommended that the
    :py:class:`ThreadLocalSingletonFactoryMixin` is used.

    """
    def __init__(self, *args, **kwargs):
        super(SingletonFactoryMixin, self).__init__(*args, **kwargs)

        self._instances = DefaultCache(self.create_instance)
        instances_lock = threading.RLock()

        def replacement_create_instance(_, name=None):
            with instances_lock:
                return self._instances[name]

        self.create_instance = replacement_create_instance


class ThreadLocalSingletonFactoryMixin(FactoryMixin):
    """
    Mixin that provides a single named instance per thread.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents and that are
    not thread safe.

    """
    def __init__(self, *args, **kwargs):
        super(ThreadLocalSingletonFactoryMixin, self).__init__(*args, **kwargs)

        self._instances = threading.local()
        create_instance = self.create_instance

        def replacement_create_instance(_, name=None):
            try:
                cache = self._instances.cache
            except AttributeError:
                cache = self._instances.cache = DefaultCache(create_instance)
            return cache[name]

        self.create_instance = replacement_create_instance
