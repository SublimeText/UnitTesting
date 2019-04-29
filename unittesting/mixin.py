from collections import ChainMap
import os
import sys
import re
from glob import glob

from .utils import OutputPanel
from .utils import JsonFile
from .utils import reload_package
from .utils import ProgressBar

import sublime


DEFAULT_SETTINGS = {
    "tests_dir": "tests",
    "pattern": "test*.py",
    "async": False,
    "deferred": False,
    "legacy_runner": True,
    "verbosity": 2,
    "output": None,
    "reload_package_on_testing": True,
    "show_reload_progress": True,
    "start_coverage_after_reload": False,
    "generate_html_report": False,
    "capture_console": False,
    "failfast": False
}


def casedpath(path):
    # path on Windows may not be properly cased
    r = glob(re.sub(r'([^:/\\])(?=[/\\]|$)', r'[\1]', path))
    return r and r[0] or path


def relative_to_spp(path):
    spp = sublime.packages_path()
    spp_real = casedpath(os.path.realpath(spp))
    for p in [path, casedpath(os.path.realpath(path))]:
        for sp in [spp, spp_real]:
            if p.startswith(sp + os.sep):
                return p[len(sp):]
    return None


class UnitTestingMixin(object):

    @property
    def current_package_name(self):
        window = sublime.active_window()
        view = window.active_view()
        if view and view.file_name():
            file_path = relative_to_spp(view.file_name())
            if file_path and file_path.endswith(".py"):
                return file_path.split(os.sep)[1]

        folders = window.folders()
        if folders and len(folders) > 0:
            first_folder = relative_to_spp(folders[0])
            if first_folder:
                return os.path.basename(first_folder)

        return None

    def input_parser(self, package):
        m = re.match(r'([^:]+):(.+)', package)
        if m:
            return m.groups()
        else:
            return (package, None)

    def prompt_package(self, callback):
        package = self.current_package_name
        if not package:
            package = ""
        view = sublime.active_window().show_input_panel(
            'Package:', package, callback, None, None)
        view.run_command("select_all")

    def load_unittesting_settings(self, package, options):
        jfile = os.path.join(sublime.packages_path(), package, "unittesting.json")
        package_settings = JsonFile(jfile).load() if os.path.exists(jfile) else {}

        return ChainMap({}, options, package_settings, DEFAULT_SETTINGS)

    def default_output(self, package):
        outputdir = os.path.join(
            sublime.packages_path(), 'User', 'UnitTesting', "tests_output")
        if not os.path.isdir(outputdir):
            os.makedirs(outputdir)
        outfile = os.path.join(outputdir, package)
        return outfile

    def load_stream(self, package, settings):
        output = settings["output"]
        if not output or output == "<panel>":
            output_panel = OutputPanel(
                'UnitTesting', file_regex=r'File "([^"]*)", line (\d+)')
            output_panel.show()
            stream = output_panel
        else:
            if not os.path.isabs(output):
                if sublime.platform() == "windows":
                    output = output.replace("/", "\\")
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
                except Exception:
                    continue
            except Exception:
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
