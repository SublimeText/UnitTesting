import os
import sys
import re

from .utils import UTSetting
from .utils import OutputPanel
from .utils import JsonFile
from .utils import reload_package
from .utils import ProgressBar

import sublime

version = sublime.version()
platform = sublime.platform()


class UnitTestingMixin(object):

    @property
    def current_project_name(self):
        """Return back the project name of the current project
        """
        window = sublime.active_window()
        view = window.active_view()
        spp = os.path.realpath(sublime.packages_path())
        if view and view.file_name():
            file_path = os.path.realpath(view.file_name())
            if file_path.startswith(spp):
                return file_path[len(spp):].split(os.sep)[1]

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

    def reload_package(self, package, show_progress=False, show_console=False):
        if show_progress:
            # a hack to run run_async of PackageReloader
            progress_bar = ProgressBar("Reloading %s" % package)
            progress_bar.start()
            window = sublime.active_window()

            console_opened = window.active_panel() == "console"
            if not console_opened and show_console:
                window.run_command("show_panel", {"panel": "console"})
            try:
                reload_package(package)
            except:
                sublime.status_message("Fail to reload {}.".format(package))
                raise
            finally:
                progress_bar.stop()

            if not console_opened and show_console:
                window.run_command("hide_panel", {"panel": "console"})

            sublime.status_message("{} reloaded.".format(package))
        else:
            reload_package(package, dummy=False)

    def remove_test_modules(self, package, tests_dir):
        modules = {}
        # make a copy of sys.modules
        for mname in sys.modules:
            modules[mname] = sys.modules[mname]

        for mname in modules:
            try:
                mpath = sys.modules[mname].__path__._path[0]
            except AttributeError:
                try:
                    mpath = os.path.dirname(sys.modules[mname].__file__)
                except:
                    continue
            except:
                continue
            tests_dir = os.path.realpath(os.path.join(sublime.packages_path(), package, tests_dir))
            if os.path.realpath(mpath).startswith(tests_dir):
                del sys.modules[mname]
