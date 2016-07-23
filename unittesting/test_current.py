import sublime
from .test_package import UnitTestingCommand


class UnitTestingCurrentProjectCommand(UnitTestingCommand):
    def run(self):
        project_name = self.current_project_name
        if not project_name:
            sublime.message_dialog("Project not found.")
            return

        UnitTestingCommand.run(self, project_name)


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
