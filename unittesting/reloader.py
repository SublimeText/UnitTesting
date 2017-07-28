import sublime_plugin
import sublime
from .mixin import UnitTestingMixin


class UnitTestingReloadCurrentProjectCommand(UnitTestingMixin, sublime_plugin.WindowCommand):

    def run(self, pkg_name=None):
        sublime.set_timeout_async(lambda: self.run_async(pkg_name))

    def run_async(self, pkg_name=None, show_console=True):
        if not pkg_name:
            pkg_name = self.current_project_name

        if pkg_name:
            self.reload_package(pkg_name, show_progress=True, show_console=True)
