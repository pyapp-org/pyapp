"""
Single file sample
"""
from pyapp.app import argument
from pyapp.app import CliApplication

APP = CliApplication()


@APP.command
@argument("OPTS", nargs="+")
def helper(opts):
    print(opts.OPTS)


if __name__ == "__main__":
    APP.dispatch()
