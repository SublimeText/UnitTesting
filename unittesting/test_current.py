import sublime
import sys
from collections import namedtuple
from .test_package import UnitTestingCommand


class UnitTestingCurrentProjectCommand(UnitTestingCommand):
    def run(self, coverage=False):
        project_name = self.current_project_name
        if not project_name:
            sublime.message_dialog("Project not found.")
            return

        UnitTestingCommand.run(self, project_name, coverage=coverage)


class UnitTestingCurrentProjectReloadCommand(UnitTestingCommand):

    def run(self, coverage=False):
        self.coverage = coverage
        # since PackageReloader is st 3 only, we have
        # sublime.set_timeout_async
        sublime.set_timeout_async(self.run_async, 1)

    def run_async(self):
        project_name = self.current_project_name
        if not project_name:
            sublime.message_dialog("Project not found.")
            return

        PackageReloader = sys.modules["PackageReloader"]
        # a hack to run run_async of PackageReloader
        w = type('', (), {})()
        setattr(w, "window", sublime.active_window())
        PackageReloader.package_reloader.PackageReloaderReloadCommand.run_async(w, project_name)
        sublime.set_timeout(
            lambda: sublime.run_command(
                "unit_testing_current_project", args={"coverage": self.coverage}))

    def is_enabled(self):
        return "PackageReloader" in sys.modules


class UnitTestingCurrentFileCommand(UnitTestingCommand):
    def run(self):
        project_name = self.current_project_name
        if not project_name:
            sublime.message_dialog("Project not found.")
            return

        test_file = self.current_test_file
        if not test_file:
            test_file = ""
        print(test_file)

        UnitTestingCommand.run(self, "{}:{}".format(project_name, test_file))
