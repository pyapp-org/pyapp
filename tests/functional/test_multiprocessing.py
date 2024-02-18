import pyapp.multiprocessing

_DATA = []


def _sample_func(a, b):
    from pyapp.conf import settings

    return f"{a}-{b}-{settings.UPPER_VALUE}-{':'.join(_DATA)}"


def sample_initializer(c, d):
    _DATA.append(c)
    _DATA.append(d)


class TestPool:
    def test_call_pool_and_ensure_settings_are_available(self):
        pool = pyapp.multiprocessing.Pool(processes=2)
        actual = pool.starmap(_sample_func, [(1, 2), (3, 4)])

        assert actual == ["1-2-foo-", "3-4-foo-"]

    def test_call_pool_and_with_custom_initializer(self):
        pool = pyapp.multiprocessing.Pool(
            processes=2, initializer=sample_initializer, initargs=("a", "b")
        )
        actual = pool.starmap(_sample_func, [(1, 2), (3, 4)])

        assert actual == ["1-2-foo-a:b", "3-4-foo-a:b"]
