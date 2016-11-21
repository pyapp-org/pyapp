from __future__ import print_function
import colorama
import sys

from pyapp.checks.registry import registry


class CheckReport(object):
    def __init__(self, verbose=False, f_out=sys.stdout, report_registry=registry):
        self.verbose = verbose
        self.f_out = f_out
        self._registry = report_registry

    def pre_callback(self, check):
        pass

    def post_callback(self, check, messages):
        pass

    def format_result(self):
        pass

    def run(self, tags=None):
        messages = self._registry.run_checks(tags, self.pre_callback, self.post_callback)

        for message in messages:
            print(message, file=self.f_out)
        
        return messages
