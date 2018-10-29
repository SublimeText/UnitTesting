import sublime
import sys
from .test_package import UnitTestingCommand
from .test_coverage import UnitTestingCoverageCommand


class UnitTestingCurrentPackageCommand(UnitTestingCommand):
    def run(self, **kwargs):
        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        sublime.set_timeout_async(
            lambda: super(UnitTestingCurrentPackageCommand, self).run(project_name, **kwargs))

    def unit_testing(self, stream, package, settings):
        parent = super(UnitTestingCurrentPackageCommand, self)
        if settings["reload_package_on_testing"]:
            self.reload_package(
                package, dummy=True, show_reload_progress=settings["show_reload_progress"])
        parent.unit_testing(stream, package, settings)


class UnitTestingCurrentPackageCoverageCommand(UnitTestingCoverageCommand):

    def run(self, **kwargs):
        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        super(UnitTestingCurrentPackageCoverageCommand, self).run(project_name, **kwargs)

    def is_enabled(self):
        return "coverage" in sys.modules


class UnitTestingCurrentFileCommand(UnitTestingCommand):
    def run(self, **kwargs):
        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        test_file = self.current_test_file
        if not test_file:
            test_file = ""

        sublime.set_timeout_async(
            lambda: super(UnitTestingCurrentFileCommand, self).run(
                "{}:{}".format(project_name, test_file),
                **kwargs
            )
        )

    def unit_testing(self, stream, package, settings):
        # ideally, we should reuse same function in UnitTestingCurrentPackageCommand
        # but it is easier to copy it to here
        parent = super(UnitTestingCurrentFileCommand, self)
        if settings["reload_package_on_testing"]:
            self.reload_package(
                package, dummy=True, show_reload_progress=settings["show_reload_progress"])
        parent.unit_testing(stream, package, settings)
