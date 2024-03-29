import abc


class BarABC(abc.ABC):
    @abc.abstractmethod
    def is_long(self):
        raise NotImplementedError()


class Bar(BarABC):
    def __init__(self, length):
        self.length = length

    def __str__(self):
        return "Bar"

    def is_long(self):
        return self.length > 30


class IronBar(Bar):
    def __str__(self):
        return "Iron Bar"


class SteelBeam:
    def __str__(self):
        return "Steel Beam"
