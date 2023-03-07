"""
Single file sample
"""
from pyapp.app import CliApplication
from pyapp.events import listen_to

APP = CliApplication()


@listen_to(APP.pre_dispatch)
def pre_dispatch(opts):
    print(opts)


@APP.default
def helper(*, bar: dict):
    print(bar)
    # print(opts.bar)


@listen_to(APP.post_dispatch)
def pre_dispatch(result, opts):
    print(result, opts)


if __name__ == "__main__":
    APP.dispatch()
