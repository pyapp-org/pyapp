from pyapp.app import argument
from pyapp.app import CliApplication
from pyapp.app.argument_actions import KeyValueAction
from pyapp.conf import settings

app = CliApplication(prog="sample", description="Sample pyApp application.")


@app.command
@argument("--verbose", action="store_true")
def foo_do(args):
    """
    Perform a foo operation.
    """
    # Use a command line argument
    if args.verbose:
        print("Doing foo verbosely!")
    else:
        print("Doing foo.")

    # Print a message from the settings file
    print(settings.FOO_MESSAGE)


class BarGroup:
    group = app.create_command_group("bar", aliases="b")

    @staticmethod
    @group.command(name="do", aliases="d")
    @argument("--repeat", type=int, default=1)
    @argument("--option", dest="options", action=KeyValueAction)
    def do_bar(args):
        for _ in range(args.repeat):
            print(f"Doing bar with {args.options}")


@app.command(name="async")
async def async_(args):
    print("Async task")


@app.default
@argument("--bananas")
def default_command(args):
    print("Bananas", args.bananas)


def main():
    app.dispatch()


if __name__ == "__main__":
    main()
