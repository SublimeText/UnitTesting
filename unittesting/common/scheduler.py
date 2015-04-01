import os
import time
import threading

import sublime
import sublime_plugin

version = sublime.version()

from ..utils import Jfile


class Unit:

    def __init__(self, package):
        self.package = package

    def run(self):
        sublime.run_command("unit_testing", {"package": self.package})


class Scheduler:

    def __init__(self):
        self.units = []
        self.j = Jfile(os.path.join(
            sublime.packages_path(),
            'User', 'UnitTesting',
            'schedule.json')
        )

    def load_schedule(self):
        self.schedule = self.j.load()
        for s in self.schedule:
            self.units.append(Unit(s['package']))

    def run(self):
        self.load_schedule()
        for u in self.units:
            u.run()
        self.clean_schedule()

    def clean_schedule(self):
        self.schedule = [
            s for s in self.schedule
            if "expire" in s and s["expire"] == "never"
        ]
        self.j.save(self.schedule)


class UnitTestingRunSchedulerCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        DeferredRun.load()
        my_scheduler = Scheduler()
        my_scheduler.run()


class DeferredRun(threading.Thread):
    loaded = False

    def __init__(self, command, args=None):
        threading.Thread.__init__(self)
        self.command = command
        self.args = args

    @staticmethod
    def load():
        DeferredRun.loaded = True

    def run(self):
        while not DeferredRun.loaded:
            sublime.set_timeout(
                lambda: sublime.run_command(self.command, self.args), 1)
            if DeferredRun.loaded:
                break
            else:
                time.sleep(0.1)

# run the schedule in later time to ensure all packages are loaded
DeferredRun("unit_testing_run_scheduler").start()
