import importlib

from pyapp.exceptions import InvalidConfiguration


class ModuleLoader(object):
    """
    Load configuration from an importable module.

    Loader will load all upper case attributes from the imported module.

    Usage:

        >>> loader = ModuleLoader("name.of.module")
        >>> settings = dict(loader)

    """
    scheme = 'python'

    def __init__(self, module):
        """
        :param module: Fully qualify python module path.
        :type module: str
        """
        assert module

        self.module = module

    def __iter__(self):
        try:
            mod = importlib.import_module(self.module)
        except ImportError as ex:
            raise InvalidConfiguration("Unable to load module: {}\n{}".format(self, ex))

        return ((k, getattr(mod, k)) for k in dir(mod) if k.isupper())

    def __str__(self):
        return "{}:{}".format(self.scheme, self.module)
