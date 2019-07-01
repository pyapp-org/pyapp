from pyapp.app import CliApplication, argument
from pyapp.app.argument_actions import KeyValueAction
from pyapp.conf import settings

import sample

app = CliApplication(sample, prog="sample", description="Sample pyApp application.")


@app.command
@argument("--verbose", action="store_true")
def foo_do(opts):
    """
    Perform a foo operation.
    """
    # Use a command line argument
    if opts.verbose:
        print("Doing foo verbosely!")
    else:
        print("Doing foo.")

    # Print a message from the settings file
    print(settings.FOO_MESSAGE)


bar_group = app.create_command_group("bar")


@bar_group.command(name="do")
@argument("--repeat", type=int, default=1)
@argument("--option", dest="options", action=KeyValueAction)
def do_bar(opts):
    for _ in range(opts.repeat):
        print(f"Doing bar with {opts.options}")


def main():
    app.dispatch()


if __name__ == "__main__":
    main()
