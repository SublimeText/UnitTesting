import os
import re

import sublime
import sublime_plugin

version = sublime.version()

from unittest import TextTestRunner
if version >= '3000':
    from .unittesting import TestLoader
    from .unittesting import DeferringTextTestRunner
    from .utils import settings as plugin_settings
    from .utils import Jfile
else:
    from unittesting import TestLoader
    from utils import settings as plugin_settings
    from utils import Jfile


# st3 has append command, it is needed for st2.
class OutputPanelInsert(sublime_plugin.TextCommand):

    def run(self, edit, characters):
        self.view.set_read_only(False)
        self.view.insert(edit, self.view.size(), characters)
        self.view.set_read_only(True)
        self.view.show(self.view.size())


class OutputPanel:

    def __init__(
        self, name, file_regex='', line_regex='', base_dir=None,
        word_wrap=False, line_numbers=False, gutter=False,
        scroll_past_end=False, syntax='Packages/Text/Plain text.tmLanguage'
    ):
        self.name = name
        self.window = sublime.active_window()
        self.output_view = self.window.get_output_panel(name)

        # default to the current file directory
        if (not base_dir and self.window.active_view()
                and self.window.active_view().file_name()):
            base_dir = os.path.dirname(self.window.active_view().file_name())

        settings = self.output_view.settings()
        settings.set("result_file_regex", file_regex)
        settings.set("result_line_regex", line_regex)
        settings.set("result_base_dir", base_dir)
        settings.set("word_wrap", word_wrap)
        settings.set("line_numbers", line_numbers)
        settings.set("gutter", gutter)
        settings.set("scroll_past_end", scroll_past_end)
        settings.set("syntax", syntax)
        self.closed = False

    def write(self, s):
        self.output_view.run_command('output_panel_insert', {'characters': s})

    def flush(self):
        pass

    def show(self):
        self.window.run_command("show_panel", {"panel": "output." + self.name})

    def close(self):
        self.closed = True
        pass


def input_parser(package):
    m = re.match(r'([^/]+)/(.+)', package)
    if m:
        return m.groups()
    else:
        return (package, "test*.py")


class UnitTestingCommand(sublime_plugin.ApplicationCommand):

    @property
    def project_name(self):
        """Return back the project name of the current project
        """

        project_name = sublime.active_window().project_file_name()
        if project_name is None:
            folders = sublime.active_window().folders()
            if len(folders) > 0:
                project_name = folders[0].rsplit(os.sep, 1)[1]
        else:
            project_name = project_name.rsplit(os.sep, 1)[1].split('.')[0]

        return project_name

    def run(self, package=None, output=None):

        if package:
            if package == "<current>":
                package = self.project_name
            plugin_settings.set("recent-package", package)

            package, pattern = input_parser(package)

            jfile = os.path.join(sublime.packages_path(), package, "unittesting.json")
            if os.path.exists(jfile):
                ss = Jfile(jfile).load()
                tests_dir = ss.get("tests_dir", "tests")
                async = ss.get("async", False)
                deferred = ss.get("deferred", False)
            else:
                tests_dir, async, deferred = "tests", False, False

            if version < '3000':
                deferred = False
                async = False

            if output == "panel":
                output_panel = OutputPanel(
                    'unittests', file_regex=r'File "([^"]*)", line (\d+)')
                output_panel.show()
                stream = output_panel
            else:
                if output:
                    outfile = output
                else:
                    outputdir = os.path.join(
                        sublime.packages_path(),
                        'User', 'UnitTesting', "tests_output"
                    )
                    if not os.path.isdir(outputdir):
                        os.makedirs(outputdir)
                    outfile = os.path.join(outputdir, package)

                if os.path.exists(outfile):
                    os.remove(outfile)
                stream = open(outfile, "w")

            if async:
                sublime.set_timeout_async(
                    lambda: self.testing(package, tests_dir, pattern, stream, False), 100)
            else:
                self.testing(package, tests_dir, pattern, stream, deferred)

        else:
            # bootstrap run() with package input
            view = sublime.active_window().show_input_panel(
                'Package:', plugin_settings.get("recent-package", "Package Name"),
                lambda x: sublime.run_command(
                    "unit_testing", {
                        "package": x,
                        "output": output
                    }), None, None
                )
            view.run_command("select_all")

    def testing(self, package, tests_dir, pattern, stream, deferred=False):
        try:
            # use custom loader which support ST2 and reloading modules
            loader = TestLoader(deferred)
            test = loader.discover(os.path.join(
                sublime.packages_path(), package, tests_dir), pattern
            )
            # use deferred test runner or default test runner
            if deferred:
                testRunner = DeferringTextTestRunner(stream, verbosity=2)
            else:
                testRunner = TextTestRunner(stream, verbosity=2)
            testRunner.run(test)
        except Exception as e:
            if not stream.closed:
                stream.write("ERROR: %s\n" % e)
        if not deferred:
            stream.close()
