from pyapp import checks, feature_flags
from pyapp.app import CliApplication

import tests.unit.sample_app

app = CliApplication(tests.unit.sample_app)


@app.command
def happy():
    print("=o)")


@app.command
def sad():
    print("=o(")
    return -2


@app.command
def cheeky(opts):
    print("=oD")
    raise KeyboardInterrupt()


@app.command
def angry(opts):
    print(">=o(")
    raise Exception("Grrrr")


@app.command
def undecided():
    if feature_flags.get("happy"):
        print("=o)")
        return 10

    elif feature_flags.get("sad", default=True):
        print("=o(")
        return 30

    else:
        print("=o|")
        return 20


plain_group = app.create_command_group("plain")


@plain_group.command(name="sample")
def plain_group_sample():
    return 1324


class ClassGroup:
    group = app.create_command_group("class")

    @staticmethod
    @group.command
    def static():
        return 1332

    @group.command(name="non-static")
    def non_static(self, arg1: int):
        return 1348 + arg1


@checks.register
def critical_check(**_):
    return checks.Critical(
        "Critical message, that is really really long and should be wrapped across lines. Actually across two no THREE "
        "lines! Now that is getting fairly full on! :)",
        "Remove critical messages",
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
            [
                "Just a tip really message.",
                "This is also a multi-paragraph hint as an example of what can be done.",
            ],
            obj="App",
        ),
    )


@checks.register
def all_good(**_):
    pass


@checks.register
def debug_check(**_):
    return checks.Debug("Debug message")


if __name__ == "__main__":
    app.dispatch()
