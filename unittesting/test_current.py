import sublime
import sys
from .test_package import UnitTestingCommand
from .test_coverage import UnitTestingCoverageCommand

version = sublime.version()
platform = sublime.platform()


class UnitTestingCurrentProjectCommand(UnitTestingCommand):
    def run(self):
        project_name = self.current_project_name
        if not project_name:
            sublime.message_dialog("Project not found.")
            return

        if version >= "3000":
            sublime.set_timeout_async(lambda: self.run_async(project_name))
        else:
            super().run(project_name)

    def run_async(self, project_name):
        self.reload_package(project_name, show_progress=True)
        orig_run = super().run
        sublime.set_timeout(lambda: orig_run(project_name))


class UnitTestingCurrentProjectCoverageCommand(UnitTestingCoverageCommand):

    def run(self):
        project_name = self.current_project_name
        if not project_name:
            sublime.message_dialog("Project not found.")
            return

        super().run(project_name)

    def is_enabled(self):
        return "coverage" in sys.modules


class UnitTestingCurrentFileCommand(UnitTestingCommand):
    def run(self):
        project_name = self.current_project_name
        if not project_name:
            sublime.message_dialog("Project not found.")
            return

        test_file = self.current_test_file
        if not test_file:
            test_file = ""

        super().run("{}:{}".format(project_name, test_file))
