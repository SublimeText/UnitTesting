import sublime, sublime_plugin
import time
import threading, os
import json, codecs

class Jfile:
    def __init__(self, fpath, encoding="utf-8"):
        self.encoding = encoding
        self.fpath = fpath

    def load(self, default=[]):
        self.fdir = os.path.dirname(self.fpath)
        if not os.path.isdir(self.fdir):
            os.makedirs(self.fdir)
        if os.path.exists(self.fpath):
            f = codecs.open(self.fpath, "r+", encoding=self.encoding)
            try:
                data = json.load(f)
            except:
                data = default
            f.close()
        else:
            f = codecs.open(self.fpath, "w+", encoding=self.encoding)
            data = default
            f.close()
        return data

    def save(self, data, indent=4):
        self.fdir = os.path.dirname(self.fpath)
        if not os.path.isdir(self.fdir):
            os.makedirs(self.fdir)
        f = codecs.open(self.fpath, "w+", encoding=self.encoding)
        f.write(json.dumps(data, ensure_ascii=False, indent=indent))
        f.close()

    def remove(self):
        if os.path.exists(self.fpath): os.remove(self.fpath)

class Unit:
    def __init__(self, package, async=False, deferred=False):
        self.package = package
        self.async = async
        self.deferred = deferred

    def run(self):
        sublime.run_command("unit_testing", {"package": self.package, "async": self.async, "deferred": self.deferred})

class Scheduler:
    def __init__(self):
        self.units = []
        self.j = Jfile(os.path.join(sublime.packages_path(), 'User', 'UnitTesting','schedule.json'))

    def load_schedule(self):
        self.schedule = self.j.load()
        for s in self.schedule:
            self.units.append(Unit(s['package'], s.get('async', False), s.get('deferred', False)))

    def run(self):
        self.load_schedule()
        for u in self.units:
            u.run()
        self.clean_schedule()

    def clean_schedule(self):
        self.schedule = [s for s in self.schedule if "expire" in s and s["expire"] == "never"]
        self.j.save(self.schedule)

class UnitTestingRunSchedulerCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        DeferredRun.shouldrun()
        my_scheduler = Scheduler()
        my_scheduler.run()

class DeferredRun(threading.Thread):
    loaded = False

    def __init__(self, command, args=None):
        threading.Thread.__init__(self)
        self.command = command
        self.args = args

    @staticmethod
    def shouldrun():
        DeferredRun.loaded = True

    def run(self):
        while not DeferredRun.loaded:
            sublime.set_timeout(lambda: sublime.run_command(self.command, self.args), 1)
            if DeferredRun.loaded:
                break
            else:
                time.sleep(0.1)

# run the schedule in later time to ensure all packages are loaded
DeferredRun("unit_testing_run_scheduler").start()
