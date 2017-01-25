from __future__ import unicode_literals


def is_iterable(obj):
    """
    Determine if an object is iterable.

    :rtype: bool

    """
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True
