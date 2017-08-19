import sublime
import sys
from .test_package import UnitTestingCommand
from .test_coverage import UnitTestingCoverageCommand

version = sublime.version()
platform = sublime.platform()


class UnitTestingCurrentPackageCommand(UnitTestingCommand):
    def run(self):
        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        sublime.set_timeout_async(lambda: self.run_async(project_name))

    def run_async(self, project_name):
        orig_run = super(UnitTestingCurrentPackageCommand, self).run
        self.reload_package(project_name, show_progress=True)
        sublime.set_timeout(lambda: orig_run(project_name))


class UnitTestingCurrentPackageCoverageCommand(UnitTestingCoverageCommand):

    def run(self):
        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        super(UnitTestingCurrentPackageCoverageCommand, self).run(project_name)

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

        super(UnitTestingCurrentFileCommand, self).run("{}:{}".format(project_name, test_file))
