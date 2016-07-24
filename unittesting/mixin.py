import os
import re
import tempfile

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

        if version >= "3000":
            project_name = sublime.active_window().project_file_name()
        else:
            project_name = None

        if project_name is None:
            folders = sublime.active_window().folders()
            if len(folders) > 0:
                project_name = folders[0].rsplit(os.sep, 1)[1]
        else:
            project_name = project_name.rsplit(os.sep, 1)[1].split('.')[0]

        return project_name

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
        coverage = kargs["coverage"] if "coverage" in kargs else None

        jfile = os.path.join(sublime.packages_path(), package, "unittesting.json")
        if os.path.exists(jfile):
            ss = JsonFile(jfile).load()
            tests_dir = ss.get("tests_dir", tests_dir)
            async = ss.get("async", async)
            deferred = ss.get("deferred", deferred)
            verbosity = ss.get("verbosity", verbosity)
            if pattern is None:
                pattern = ss.get("pattern", pattern)
            if not output:
                output = ss.get("output", "<panel>")
            capture_console = ss.get("capture_console", False)
            coverage = ss.get("coverage", False)

        if pattern is None:
            pattern = "test*.py"

        if output is None:
            output = "<panel>"

        if version < '3000':
            async = False
        if version < '3000' or platform == "windows":
            coverage = False

        return {
            "tests_dir": tests_dir,
            "async": async,
            "deferred": deferred,
            "verbosity": verbosity,
            "pattern": pattern,
            "output": output,
            "capture_console": capture_console,
            "coverage": coverage
        }

    def default_output(self, package):
        outputdir = os.path.join(
            sublime.packages_path(), 'User', 'UnitTesting', "tests_output")
        if not os.path.isdir(outputdir):
            os.makedirs(outputdir)
        outfile = os.path.join(outputdir, package)
        return outfile

    def load_stream(self, package, output):
        if output == "<panel>":
            output_panel = OutputPanel(
                'UnitTesting', file_regex=r'File "([^"]*)", line (\d+)')
            output_panel.show()
            stream = output_panel
        elif output == "<tempfile>":
            stream = tempfile.NamedTemporaryFile(mode="w", delete=False)
            window = sublime.active_window()
            view = window.active_view()
            window.open_file(stream.name)
            window.focus_view(view)
        else:
            if not output or output == "<file>":
                outfile = self.default_output(package)
            else:
                outfile = output
            if not os.path.isabs(outfile):
                if sublime.platform() == "windows":
                    outfile.replace("/", "\\")
                outfile = os.path.join(sublime.packages_path(), package, outfile)
            if os.path.exists(outfile):
                os.remove(outfile)
            stream = open(outfile, "w")

        return stream
