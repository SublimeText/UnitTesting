import os
import sublime
import sublime_plugin
from .utils import JsonFile


class Unit:

    def __init__(self, s):
        self.syntax_test = s.get('syntax_test', False)
        self.syntax_compatibility = s.get('syntax_compatibility', False)
        self.color_scheme_test = s.get('color_scheme_test', False)
        self.coverage = s.get('coverage', False)
        self.kwargs = {"package": s['package']}
        tcp_port = s.get('tcp_port')
        if tcp_port is not None:
            self.kwargs["tcp_port"] = tcp_port

    def run(self):
        if self.syntax_test:
            command = "unit_testing_syntax"
        elif self.syntax_compatibility:
            command = "unit_testing_syntax_compatibility"
        elif self.color_scheme_test:
            command = "unit_testing_color_scheme"
        elif self.coverage:
            command = "unit_testing_coverage"
        else:
            command = "unit_testing"
        sublime.run_command(command, self.kwargs)


class Scheduler:

    def __init__(self):
        self.units = []
        self.j = JsonFile(os.path.join(
            sublime.packages_path(),
            'User', 'UnitTesting',
            'schedule.json')
        )

    def load_schedule(self):
        self.schedule = self.j.load()
        for s in self.schedule:
            self.units.append(Unit(s))

    def run(self):
        self.load_schedule()
        for u in self.units:
            u.run()
        self.clean_schedule()

    def clean_schedule(self):
        self.j.save([])


class UnitTestingRunSchedulerCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        Scheduler().run()


class UnitTestingPingCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        ready_file = os.path.join(
            sublime.packages_path(), "User", "UnitTesting", "ready")
        with open(ready_file, 'w') as fp:
            print("ready", file=fp)
