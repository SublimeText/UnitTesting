import os
import re
import sublime
import sublime_plugin
import threading

from collections import ChainMap, deque
from fnmatch import fnmatch
from glob import glob

DEFAULT_SETTINGS = {
    # input
    "tests_dir": "tests",
    "pattern": "test*.py",
    # runner
    "async": False,  # deprecated
    "deferred": True,
    "condition_timeout": 4000,
    "failfast": False,
    # output
    "output": None,
    "verbosity": 2,
    "warnings": "default",
    "capture_console": False,
    # reloader
    "reload_package_on_testing": True,
    # coverage
    "coverage": False,
    "coverage_on_worker_thread": False,  # experimental
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


class OutputPanel:
    def __init__(
        self,
        window,
        name,
        file_regex="",
        line_regex="",
        base_dir=None,
        word_wrap=False,
        line_numbers=False,
        gutter=False,
        scroll_past_end=False,
    ):
        self.name = name
        self.window = window
        self.output_view = window.create_output_panel(name)

        # default to the current file directory
        if not base_dir:
            view = window.active_view()
            if view:
                file_name = view.file_name()
                if file_name:
                    base_dir = os.path.dirname(file_name)

        settings = self.output_view.settings()
        settings.set("result_file_regex", file_regex)
        settings.set("result_line_regex", line_regex)
        settings.set("result_base_dir", base_dir)
        settings.set("word_wrap", word_wrap)
        settings.set("line_numbers", line_numbers)
        settings.set("gutter", gutter)
        settings.set("scroll_past_end", scroll_past_end)

        # make sure to apply settings
        self.output_view = window.create_output_panel(name)
        self.output_view.assign_syntax("unit-testing-test-result.sublime-syntax")
        self.output_view.set_read_only(True)
        self.closed = False

        self.text_queue_lock = threading.Lock()
        self.text_queue = deque()

    def write(self, s):
        with self.text_queue_lock:
            self.text_queue.append(s)

    def writeln(self, s):
        self.write(s + "\n")

    def _write(self):
        text = ""
        with self.text_queue_lock:
            while self.text_queue:
                text += self.text_queue.popleft()

        self.output_view.run_command("append", {"characters": text, "force": True})
        self.output_view.show(self.output_view.size())

    def flush(self):
        self._write()

    def show(self):
        self.window.run_command("show_panel", {"panel": "output." + self.name})

    def close(self):
        self.flush()
        self.closed = True


class StdioSplitter:
    def __init__(self, io, stream):
        self.io = io
        self.stream = stream

    def write(self, data):
        self.io.write(data)
        self.stream.write(data)

    def writeln(self, s):
        self.write(s + "\n")

    def flush(self):
        self.io.flush()
        self.stream.flush()


class BaseUnittestingCommand(sublime_plugin.WindowCommand):
    def current_package_name(self):
        view = self.window.active_view()
        if view and view.file_name():
            file_path = relative_to_spp(view.file_name())
            if file_path:
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
                self.window, "UnitTesting", file_regex=r'File "([^"]*)", line (\d+)'
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
