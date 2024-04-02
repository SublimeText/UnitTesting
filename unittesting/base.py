import os
import re
import sublime
import sublime_plugin

from collections import ChainMap
from fnmatch import fnmatch
from glob import glob

from .utils import OutputPanel

DEFAULT_SETTINGS = {
    # input
    "tests_dir": "tests",
    "pattern": "test*.py",
    # runner
    "async": False,                       # deprecated
    "deferred": True,
    "condition_timeout": 4000,
    "failfast": False,
    # output
    "output": None,
    "verbosity": 2,
    "capture_console": False,
    # reloader
    "reload_package_on_testing": True,
    # coverage
    "coverage": False,
    "coverage_on_worker_thread": False,   # experimental
    "generate_html_report": False,
    "generate_xml_report": False,
}

DONE_MESSAGE = "UnitTesting: Done.\n"


def casedpath(path):
    # path on Windows may not be properly cased
    r = glob(re.sub(r"([^:/\\])(?=[/\\]|$)", r"[\1]", path))
    return r and r[0] or path


def relative_to_spp(path):
    spp = sublime.packages_path()
    spp_real = casedpath(os.path.realpath(spp))
    for p in [path, casedpath(os.path.realpath(path))]:
        for sp in [spp, spp_real]:
            if p.startswith(sp + os.sep):
                return p[len(sp) :]
    return None


class BaseUnittestingCommand(sublime_plugin.WindowCommand):
    def current_package_name(self):
        view = self.window.active_view()
        if view and view.file_name():
            file_path = relative_to_spp(view.file_name())
            if file_path and file_path.endswith(".py"):
                return file_path.split(os.sep)[1]

        folders = self.window.folders()
        if folders and len(folders) > 0:
            first_folder = relative_to_spp(folders[0])
            if first_folder:
                return os.path.basename(first_folder)

        return None

    def current_test_file(self, pattern):
        view = self.window.active_view()
        if view:
            current_file = os.path.basename(view.file_name() or "")
            if current_file and fnmatch(current_file, pattern):
                self.window.settings().set("UnitTesting.last_test_file", current_file)
                return current_file

        return self.window.settings().get("UnitTesting.last_test_file")

    def load_stream(self, package, settings):
        output = settings["output"]
        if not output or output == "<panel>":
            output_panel = OutputPanel(
                self.window, "exec", file_regex=r'File "([^"]*)", line (\d+)'
            )
            output_panel.show()
            return output_panel

        if not os.path.isabs(output):
            output = os.path.join(sublime.packages_path(), package, output)
        os.makedirs(os.path.dirname(output), exist_ok=True)
        return open(output, "w", encoding="utf-8")

    def load_unittesting_settings(self, package, options):
        file_name = os.path.join(sublime.packages_path(), package, "unittesting.json")

        try:
            with open(file_name, "r", encoding="utf-8") as fp:
                json_data = sublime.decode_value(fp.read())
                if not isinstance(json_data, dict):
                    raise ValueError("unittesting.json content must be an object!")
        except FileNotFoundError:
            json_data = {}
        except Exception as e:
            json_data = {}
            print("ERROR: Unable to load 'unittesting.json'\n  ", str(e))

        return ChainMap(options, json_data, DEFAULT_SETTINGS)
