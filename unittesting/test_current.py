import sublime
import sys
from .test_package import UnitTestingCommand
from .test_coverage import UnitTestingCoverageCommand


class UnitTestingCurrentPackageCommand(UnitTestingCommand):
    def run(self):
        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        sublime.set_timeout_async(
            lambda: super(UnitTestingCurrentPackageCommand, self).run(project_name))


class UnitTestingCurrentPackageCoverageCommand(UnitTestingCoverageCommand):

    def run(self):
        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        sublime.set_timeout_async(
            super(UnitTestingCurrentPackageCoverageCommand, self).run(project_name))

    def is_enabled(self):
        return "coverage" in sys.modules


class UnitTestingCurrentFileCommand(UnitTestingCommand):
    def run(self):
        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        test_file = self.current_test_file
        if not test_file:
            test_file = ""

        sublime.set_timeout_async(
            lambda: super(UnitTestingCurrentFileCommand, self).run("{}:{}".format(project_name, test_file)))
