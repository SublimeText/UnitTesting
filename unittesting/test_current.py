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

    def unit_testing(self, stream, package, settings):
        parent = super(UnitTestingCurrentPackageCommand, self)
        if settings["reload_package_on_testing"]:
            self.reload_package(
                package, dummy=True, show_reload_progress=settings["show_reload_progress"])
        parent.unit_testing(stream, package, settings)


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
