import sublime_plugin

from .utils import switchable


class UnitTestingTestSuiteCommand(sublime_plugin.WindowCommand):

    def run(self, **kwargs):
        self.window.run_command('unit_testing_current_package', kwargs)


class UnitTestingTestFileCommand(sublime_plugin.WindowCommand):

    def run(self, **kwargs):
        self.window.run_command('unit_testing_current_file', kwargs)


class UnitTestingTestLastCommand(sublime_plugin.WindowCommand):

    def run(self, **kwargs):
        raise NotImplementedError()


class UnitTestingTestNearestCommand(sublime_plugin.WindowCommand):

    def run(self, **kwargs):
        self.window.run_command('unit_testing_current_file', kwargs)


class UnitTestingTestResultsCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.run_command('show_panel', {'panel': 'output.UnitTesting'})


class UnitTestingTestCancelCommand(sublime_plugin.WindowCommand):

    def run(self):
        raise NotImplementedError()


class UnitTestingTestVisitCommand(sublime_plugin.WindowCommand):

    def run(self):
        raise NotImplementedError()


class UnitTestingTestSwitchCommand(sublime_plugin.WindowCommand):

    def run(self):
        switchable.open(self.window)
