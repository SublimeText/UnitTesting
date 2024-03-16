import os
import threading
import time
import sublime
import sublime_plugin
from .utils import JsonFile


class Unit:

    def __init__(self, s):
        self.package = s['package']

        self.output = s.get('output', None)
        self.syntax_test = s.get('syntax_test', False)
        self.syntax_compatibility = s.get('syntax_compatibility', False)
        self.color_scheme_test = s.get('color_scheme_test', False)
        self.coverage = s.get('coverage', False)

    def run(self):
        if self.syntax_test:
            sublime.run_command("unit_testing_syntax", {
                "package": self.package,
                "output": self.output
            })
        elif self.syntax_compatibility:
            sublime.run_command("unit_testing_syntax_compatibility", {
                "package": self.package,
                "output": self.output
            })
        elif self.color_scheme_test:
            sublime.run_command("unit_testing_color_scheme", {
                "package": self.package,
                "output": self.output
            })
        elif self.coverage:
            sublime.run_command("unit_testing_coverage", {
                "package": self.package,
                "output": self.output,
                "generate_xml_report": True
            })
        else:
            sublime.run_command("unit_testing", {
                "package": self.package,
                "output": self.output
            })


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
    ready = False

    def run(self):
        UnitTestingRunSchedulerCommand.ready = True
        scheduler = Scheduler()
        sublime.set_timeout(scheduler.run, 2000)


def try_running_scheduler():
    while not UnitTestingRunSchedulerCommand.ready:
        sublime.set_timeout(
            lambda: sublime.run_command("unit_testing_run_scheduler"), 1)

        time.sleep(1)


def run_scheduler():
    UnitTestingRunSchedulerCommand.ready = False
    th = threading.Thread(target=try_running_scheduler)
    th.start()
