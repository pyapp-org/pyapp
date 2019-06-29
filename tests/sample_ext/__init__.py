"""
A Sample Extension
"""


class SampleExtension:
    """
    Sample Extension
    """

    default_settings = ".default_settings"
    checks = ".checks"

    ready_called = False
    register_commands_called = False

    def ready(self):
        self.ready_called = True

    def register_commands(self, group):
        self.register_commands_called = group
