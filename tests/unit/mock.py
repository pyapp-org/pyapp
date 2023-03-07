class _AnyInstanceOf:
    """
    A helper object that compares the type of anything.

    For use with mock when you want a scoped any eg::

        mock.assert_called_with(InstanceOf(list))

    """

    def __init__(self, type_):
        self.type = type_

    def __eq__(self, other):
        return isinstance(other, self.type)

    def __ne__(self, other):
        return not isinstance(other, self.type)

    def __repr__(self):
        return f"<InstanceOf {self.type!r}>"

    __hash__ = None


ANY_INSTANCE_OF = _AnyInstanceOf
