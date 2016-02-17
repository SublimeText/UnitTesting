import os
import time
import threading

import sublime
import sublime_plugin

version = sublime.version()

from ..utils import JsonFile


class Unit:

    def __init__(self, package):
        self.package = package

    def run(self):
        sublime.run_command("unit_testing", {"package": self.package, "output": "<file>"})


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
        DeferredThread.load()
        my_scheduler = Scheduler()
        my_scheduler.run()


class DeferredThread(threading.Thread):
    loaded = False

    def __init__(self, command, args=None):
        threading.Thread.__init__(self)
        self.command = command
        self.args = args

    @staticmethod
    def load():
        DeferredThread.loaded = True

    def run(self):
        while not DeferredThread.loaded:
            sublime.set_timeout(
                lambda: sublime.run_command(self.command, self.args), 1)
            if DeferredThread.loaded:
                break
            else:
                time.sleep(0.1)


def deferred_run(command, args=None):
    th = DeferredThread(command, args)
    th.start()
