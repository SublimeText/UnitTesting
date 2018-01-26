from fnmatch import fnmatch
import os
import sys

import sublime

from .package import UnitTestingCommand
from .coverage import UnitTestingCoverageCommand


class UnitTestingCurrentPackageCommand(UnitTestingCommand):
    fallback33 = "unit_testing33_current_package"

    def run(self, **kwargs):
        if kwargs.get('coverage'):
            sublime.active_window().run_command('unit_testing_current_package_coverage')
            return

        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        kwargs["package"] = project_name

        sublime.set_timeout_async(
            lambda: super(UnitTestingCurrentPackageCommand, self).run(**kwargs))

    def unit_testing(self, stream, package, settings):
        parent = super(UnitTestingCurrentPackageCommand, self)
        if settings["reload_package_on_testing"]:
            self.reload_package(
                package, dummy=True, show_reload_progress=settings["show_reload_progress"])

        sublime.set_timeout(lambda: parent.unit_testing(stream, package, settings))


class UnitTestingCurrentFileCommand(UnitTestingCommand):
    fallback33 = "unit_testing33_current_file"

    def run(self, **kwargs):
        if kwargs.get('coverage'):
            sublime.active_window().run_command('unit_testing_current_file_coverage')
            return

        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        window = sublime.active_window()
        if not window:
            return

        view = window.active_view()

        settings = self.load_unittesting_settings(project_name, kwargs)
        current_file = (view and view.file_name()) or ''
        file_name = os.path.basename(current_file)
        if file_name and fnmatch(file_name, settings['pattern']):
            test_file = file_name
            window.settings().set('UnitTesting.last_test_file', test_file)
        else:
            test_file = (
                window.settings().get('UnitTesting.last_test_file')
                or current_file
            )

        if not test_file:
            sublime.message_dialog('Cannot determine test file name.')
            return

        if not test_file.startswith('test_'):
            test_file = 'test_' + test_file

        kwargs["package"] = "{}:{}".format(project_name, test_file)

        sublime.set_timeout_async(
            lambda: super(UnitTestingCurrentFileCommand, self).run(**kwargs)
        )

    def unit_testing(self, stream, package, settings):
        # ideally, we should reuse same function in UnitTestingCurrentPackageCommand
        # but it is easier to copy it to here
        parent = super(UnitTestingCurrentFileCommand, self)
        if settings["reload_package_on_testing"]:
            self.reload_package(
                package, dummy=True, show_reload_progress=settings["show_reload_progress"])

        sublime.set_timeout(lambda: parent.unit_testing(stream, package, settings))


class UnitTestingCurrentPackageCoverageCommand(UnitTestingCoverageCommand):
    fallback33 = "unit_testing33_current_package_coverage"

    def run(self, **kwargs):
        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        kwargs["package"] = project_name

        super(UnitTestingCurrentPackageCoverageCommand, self).run(**kwargs)


class UnitTestingCurrentFileCoverageCommand(UnitTestingCoverageCommand):
    fallback33 = "unit_testing33_current_file_coverage"

    def run(self, **kwargs):
        project_name = self.current_package_name
        if not project_name:
            sublime.message_dialog("Cannot determine package name.")
            return

        window = sublime.active_window()
        if not window:
            return

        view = window.active_view()

        settings = self.load_unittesting_settings(project_name, kwargs)
        current_file = (view and view.file_name()) or ''
        file_name = os.path.basename(current_file)
        if file_name and fnmatch(file_name, settings['pattern']):
            test_file = file_name
            window.settings().set('UnitTesting.last_test_file', test_file)
        else:
            test_file = (
                window.settings().get('UnitTesting.last_test_file')
                or current_file
            )

        if not test_file:
            sublime.message_dialog('Cannot determine test file name.')
            return

        if not test_file.startswith('test_'):
            test_file = 'test_' + test_file

        kwargs["package"] = "{}:{}".format(project_name, test_file)

        super(UnitTestingCurrentFileCoverageCommand, self).run(**kwargs)
