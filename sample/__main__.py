from pyapp.app import CliApplication, argument
from pyapp.conf import settings

import sample

app = CliApplication(sample, prog="sample", description="Sample pyApp application.")


@app.command
@argument("--verbose", action="store_true")
def do_foo(opts):
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


if __name__ == "__main__":
    app.dispatch()
