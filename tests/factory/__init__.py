class Bar(object):
    def __init__(self, length):
        self.length = length

    def __str__(self):
        return 'Bar'


class IronBar(Bar):
    def __str__(self):
        return 'Iron Bar'
