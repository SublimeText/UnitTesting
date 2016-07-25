import os
import threading
import time
import sublime
import sublime_plugin
from .utils import JsonFile


class Unit:

    def __init__(self, s):
        self.package = s['package']
        self.output = s['output'] if 'output' in s else None
        self.syntax_test = s['syntax_test'] if 'syntax_test' in s else None
        self.coverage = s['coverage'] if 'coverage' in s else None

    def run(self):
        if self.syntax_test:
            sublime.run_command("unit_testing_syntax", {
                "package": self.package,
                "output": self.output
            })
        elif self.coverage:
                sublime.run_command("unit_testing_coverage", {
                    "package": self.package,
                    "output": self.output,
                    "covdata": True
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
        scheduler.run()


def try_running_scheduler():
    while not UnitTestingRunSchedulerCommand.ready:
        sublime.set_timeout(
            lambda: sublime.run_command("unit_testing_run_scheduler"), 1)
        if UnitTestingRunSchedulerCommand.ready:
            break
        else:
            time.sleep(0.5)


def run_scheduler():
    th = threading.Thread(target=try_running_scheduler)
    th.start()
