import os
import sys
import re

from .utils import UTSetting
from .utils import OutputPanel
from .utils import JsonFile

import sublime

version = sublime.version()
platform = sublime.platform()


class UnitTestingMixin:

    @property
    def current_project_name(self):
        """Return back the project name of the current project
        """
        folders = sublime.active_window().folders()
        if folders and len(folders) > 0:
            return os.path.basename(folders[0])
        else:
            project_file_name = sublime.active_window().project_file_name()
            return os.path.splitext(os.path.basename(project_file_name))[0]

    @property
    def recent_package(self):
        return UTSetting.get("recent-package", "Package Name")

    @recent_package.setter
    def recent_package(self, package):
        UTSetting.set("recent-package", package)

    @property
    def current_test_file(self):
        current_file = sublime.active_window().active_view().file_name()
        if current_file and current_file.endswith(".py"):
            current_file = os.path.basename(current_file)
        return current_file

    def input_parser(self, package):
        m = re.match(r'([^:]+):(.+)', package)
        if m:
            return m.groups()
        else:
            return (package, None)

    def prompt_package(self, callback):
        package = self.recent_package

        def _callback(package):
            self.recent_package = package
            callback(package)

        view = sublime.active_window().show_input_panel(
            'Package:', package, _callback, None, None)
        view.run_command("select_all")

    def load_settings(self, package, pattern=None, **kargs):
        # default settings
        tests_dir = "tests"
        async = False
        deferred = False
        verbosity = 2
        output = kargs["output"] if "output" in kargs else None
        capture_console = False

        jfile = os.path.join(sublime.packages_path(), package, "unittesting.json")
        if os.path.exists(jfile):
            ss = JsonFile(jfile).load()
            tests_dir = ss.get("tests_dir", tests_dir)
            async = ss.get("async", async)
            deferred = ss.get("deferred", deferred)
            verbosity = ss.get("verbosity", verbosity)
            capture_console = ss.get("capture_console", False)
            if pattern is None:
                pattern = ss.get("pattern")
            if not output:
                output = ss.get("output")

        if pattern is None:
            pattern = "test*.py"

        if version < '3000':
            async = False

        return {
            "tests_dir": tests_dir,
            "async": async,
            "deferred": deferred,
            "verbosity": verbosity,
            "pattern": pattern,
            "output": output,
            "capture_console": capture_console
        }

    def default_output(self, package):
        outputdir = os.path.join(
            sublime.packages_path(), 'User', 'UnitTesting', "tests_output")
        if not os.path.isdir(outputdir):
            os.makedirs(outputdir)
        outfile = os.path.join(outputdir, package)
        return outfile

    def load_stream(self, package, output):
        if not output or output == "<panel>":
            output_panel = OutputPanel(
                'UnitTesting', file_regex=r'File "([^"]*)", line (\d+)')
            output_panel.show()
            stream = output_panel
        else:
            if not os.path.isabs(output):
                if sublime.platform() == "windows":
                    output.replace("/", "\\")
                output = os.path.join(sublime.packages_path(), package, output)
            if os.path.exists(output):
                os.remove(output)
            stream = open(output, "w")

        return stream

    def reload_package(self, package, interface=False):
        if "PackageReloader" in sys.modules:
            pr_settings = sublime.load_settings("package_reloader.sublime-settings")
            open_console = pr_settings.get("open_console")
            pr_settings.set("open_console", False)
            if interface:
                PackageReloader = sys.modules["PackageReloader"]
                # a hack to run run_async of PackageReloader
                w = type('', (), {})()
                setattr(w, "window", sublime.active_window())
                PackageReloader.package_reloader.PackageReloaderReloadCommand.run_async(w, package)
            else:
                sys.modules["PackageReloader"].reloader.reload_package(package, dummy=False)

            pr_settings.set("open_console", open_console)
