"""
CLI Interface
~~~~~~~~~~~~~

"""
from pyapp.app import Arg
from pyapp.app import argument
from pyapp.app import CliApplication
from pyapp.app.argument_actions import KeyValueAction
from pyapp.conf import settings

APP = CliApplication(prog="sample", description="Sample pyApp application.")


@APP.command
def foo_do(*, verbose: bool = False):
    """
    Perform a foo operation.
    """
    # Use a command line argument
    if verbose:
        print("Doing foo verbosely!")
    else:
        print("Doing foo.")

    # Print a message from the settings file
    print(settings.FOO_MESSAGE)


class BarGroup:
    group = APP.create_command_group("bar", aliases="b")

    @staticmethod
    @group.command(name="do", aliases="d")
    def do_bar(
        *, repeat: int = 1, options: dict = Arg(name="option", action=KeyValueAction)
    ):
        for _ in range(repeat):
            print(f"Doing bar with {options}")


@APP.command(name="async")
async def async_():
    print("Async task")


@APP.default
@argument("--bananas")
def default_command(args, *, bananas=None):
    print("Bananas", args.bananas)


main = APP.dispatch
