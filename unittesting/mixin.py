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
    def current_package_name(self):
        """Return back the name of the current package."""
        window = sublime.active_window()
        view = window.active_view()
        spp = os.path.realpath(sublime.packages_path())
        if view and view.file_name():
            file_path = os.path.realpath(view.file_name())
            if file_path.startswith(spp):
                return file_path[len(spp):].split(os.sep)[1]

        folders = sublime.active_window().folders()
        if folders and len(folders) > 0:
            first_folder = os.path.realpath(folders[0])
            if first_folder.startswith(spp):
                return os.path.basename(first_folder)

        return None

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
        reload_package_on_testing = True
        show_reload_progress = True
        output = kargs["output"] if "output" in kargs else None
        capture_console = False

        jfile = os.path.join(sublime.packages_path(), package, "unittesting.json")
        if os.path.exists(jfile):
            ss = JsonFile(jfile).load()
            tests_dir = ss.get("tests_dir", tests_dir)
            async = ss.get("async", async)
            deferred = ss.get("deferred", deferred)
            verbosity = ss.get("verbosity", verbosity)
            reload_package_on_testing = ss.get(
                "reload_package_on_testing", reload_package_on_testing)
            show_reload_progress = ss.get("show_reload_progress", show_reload_progress)
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
            "reload_package_on_testing": reload_package_on_testing,
            "show_reload_progress": show_reload_progress,
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

    def reload_package(self, package, dummy=False, show_reload_progress=False):
        if show_reload_progress:
            progress_bar = ProgressBar("Reloading %s" % package)
            progress_bar.start()

            try:
                reload_package(package, dummy=dummy, verbose=True)
            except Exception:
                sublime.status_message("Fail to reload {}.".format(package))
            finally:
                progress_bar.stop()

            sublime.status_message("{} reloaded.".format(package))
        else:
            reload_package(package, dummy=dummy, verbose=False)

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

            tests_dir = os.path.join(sublime.packages_path(), package, tests_dir)
            real_tests_dir = os.path.realpath(tests_dir)
            if os.path.realpath(mpath).startswith(real_tests_dir):
                del sys.modules[mname]

            # remove tests dir in sys.path
            if tests_dir in sys.path:
                sys.path.remove(tests_dir)
            elif real_tests_dir in sys.path:
                sys.path.remove(real_tests_dir)
