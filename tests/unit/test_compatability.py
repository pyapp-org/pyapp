import pytest
from pyapp import compatability


def test_async_run__not_a_coroutine():
    """
    Given a function that is not async raise a ValueError
    """

    def example():
        pass

    with pytest.raises(ValueError):
        compatability.async_run(example)
