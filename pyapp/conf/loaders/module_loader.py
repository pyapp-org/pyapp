import importlib


class ModuleLoader(object):
    """
    Load configuration from an importable module.

    Usage:

        >>> ModuleLoader("name.of.module")

    """
    def __init__(self, module):
        self.module = module

    def __str__(self):
        return "Module:{}".format(self.module)

    def __iter__(self):
        if not self.module:
            raise Exception("Unable to load module: {}".format(self))

        try:
            mod = importlib.import_module(self.module)
        except ImportError as ex:
            raise Exception("Unable to load module: {}\n{}".format(self, ex))

        return ((k, getattr(mod, k)) for k in dir(mod) if k.isupper())
