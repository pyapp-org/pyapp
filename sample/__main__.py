from typing import Dict

from pyapp.app import argument
from pyapp.app import CliApplication, Arg
from pyapp.app.argument_actions import KeyValueAction
from pyapp.conf import settings

app = CliApplication(prog="sample", description="Sample pyApp application.")


@app.command
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
    group = app.create_command_group("bar", aliases="b")

    @staticmethod
    @group.command(name="do", aliases="d")
    def do_bar(*, repeat: int = 1, options: dict = Arg(name="option", action=KeyValueAction)):
        for _ in range(repeat):
            print(f"Doing bar with {options}")


@app.command(name="async")
async def async_():
    print("Async task")


@app.default
@argument("--bananas")
def default_command(args, *, bananas=None):
    print("Bananas", args.bananas)


def main():
    app.dispatch()


if __name__ == "__main__":
    main()
