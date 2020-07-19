"""
Single file sample
"""
from pyapp.app import argument
from pyapp.app import CliApplication
from pyapp.app import CommandOptions
from pyapp.app import KeyValueAction

APP = CliApplication()


@APP.default
def helper(*, bar: dict):
    print(bar)
    # print(opts.bar)


if __name__ == "__main__":
    APP.dispatch()
