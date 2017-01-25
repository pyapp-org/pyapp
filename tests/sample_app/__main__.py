from __future__ import absolute_import, print_function, unicode_literals

from pyapp import checks
from pyapp.app import CliApplication

import tests.sample_app

app = CliApplication(tests.sample_app)


@checks.register
def critical_check(**_):
    return checks.Critical(
        "Critical message, that is really really long and should be wrapped across lines. Actually across two no THREE "
        "lines! Now that is getting fairly full on! :)",
        "Remove critical messages"
    )


@checks.register("skippable")
def error_check(**_):
    return checks.Error("Error message", obj="App")


@checks.register
def double_check(**_):
    return (
        checks.Warn("Warn message", "Remove warning messages", obj="App"),
        checks.Info(
            "Info message",
            ["Just a tip really message.", "This is also a multi-paragraph hint as an example of what can be done."],
            obj="App"
        ),
    )


@checks.register
def all_good(**_):
    pass


@checks.register
def debug_check(**_):
    return checks.Debug("Debug message")


if __name__ == '__main__':
    app.dispatch()
