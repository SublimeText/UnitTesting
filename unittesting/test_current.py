import sublime
import sys
from collections import namedtuple
from .test_package import UnitTestingCommand
from .test_coverage import UnitTestingCoverageCommand


class UnitTestingCurrentProjectCommand(UnitTestingCommand):
    def run(self):
        project_name = self.current_project_name
        if not project_name:
            sublime.message_dialog("Project not found.")
            return

        UnitTestingCommand.run(self, project_name)


class UnitTestingCurrentProjectReloadCommand(UnitTestingCommand):

    def run(self):
        # since PackageReloader is st 3 only, we have
        # sublime.set_timeout_async
        sublime.set_timeout_async(self.run_async, 1)

    def run_async(self):
        project_name = self.current_project_name
        if not project_name:
            sublime.message_dialog("Project not found.")
            return

        self.reload_package(project_name, interface=True)
        UnitTestingCommand.run(self, project_name)

    def is_enabled(self):
        return "PackageReloader" in sys.modules


class UnitTestingCurrentProjectCoverageCommand(UnitTestingCoverageCommand):

    def run(self):
        # since PackageReloader is st 3 only, we have
        # sublime.set_timeout_async
        sublime.set_timeout_async(self.run_async, 1)

    def run_async(self):
        project_name = self.current_project_name
        if not project_name:
            sublime.message_dialog("Project not found.")
            return

        UnitTestingCoverageCommand.run(self, project_name)

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
