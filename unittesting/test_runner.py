import sys
import os
import re
import tempfile
import logging
from unittest import TextTestRunner
from .core import TestLoader
from .core import DeferringTextTestRunner
from .utils import UTSetting
from .utils import OutputPanel
from .utils import JsonFile

import sublime
import sublime_plugin

version = sublime.version()

if version >= "3103":
    import sublime_api


def input_parser(package):
    m = re.match(r'([^:]+):(.+)', package)
    if m:
        return m.groups()
    else:
        return (package, None)


class UnitTestingCommand(sublime_plugin.ApplicationCommand):

    @property
    def project_name(self):
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

    def default_output(self, package):
        outputdir = os.path.join(
            sublime.packages_path(),
            'User', 'UnitTesting', "tests_output"
        )
        if not os.path.isdir(outputdir):
            os.makedirs(outputdir)
        outfile = os.path.join(outputdir, package)
        return outfile

    def prompt_package(self, package, output, syntax_test):
        view = sublime.active_window().show_input_panel(
            'Package:', package,
            lambda x: sublime.run_command(
                "unit_testing", {
                    "package": x,
                    "output": output,
                    "syntax_test": syntax_test
                }), None, None
            )
        view.run_command("select_all")

    def load_package(self, package, output, syntax_test):
        if not package:
            # bootstrap run() with package input
            package = UTSetting.get("recent-package", "Package Name")
            self.prompt_package(package, output, syntax_test)
            return

        if package == "<current>":
            package = self.project_name
        if package:
            UTSetting.set("recent-package", package)
        else:
            sublime.message_dialog("Cannot find current package.")
            return

        return input_parser(package)

    def load_settings(self, package, pattern, output):
        jfile = os.path.join(sublime.packages_path(), package, "unittesting.json")
        if os.path.exists(jfile):
            ss = JsonFile(jfile).load()
            tests_dir = ss.get("tests_dir", "tests")
            async = ss.get("async", False)
            deferred = ss.get("deferred", False)
            verbosity = ss.get("verbosity", 2)
            if pattern is None:
                pattern = ss.get("pattern", pattern)
            if not output:
                output = ss.get("output", "<panel>")
            capture_console = ss.get("capture_console", False)
        else:
            tests_dir = "tests"
            async = False
            deferred = False
            verbosity = 2
            capture_console = False
            if not output:
                output = "<panel>"

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

    def load_stream(self, package, output):
        if output == "<panel>":
            output_panel = OutputPanel(
                'unittests', file_regex=r'File "([^"]*)", line (\d+)')
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

    def run(self, package=None, output=None, syntax_test=False):

        package, pattern = self.load_package(package, output, syntax_test)
        settings = self.load_settings(package, pattern, output)
        stream = self.load_stream(package, settings["output"])

        if syntax_test:
            self.syntax_testing(stream, package)
        else:
            if settings["async"]:
                sublime.set_timeout_async(
                    lambda: self.unit_testing(stream, package, settings), 100)
            else:
                self.unit_testing(stream, package, settings)

    def unit_testing(self, stream, package, settings):
        stdout = sys.stdout
        stderr = sys.stderr
        handler = logging.StreamHandler(stream)
        if settings["capture_console"]:
            logging.root.addHandler(handler)
            sys.stdout = stream
            sys.stderr = stream

        testRunner = None

        try:
            # use custom loader which support ST2 and reloading modules
            loader = TestLoader(settings["deferred"])
            test = loader.discover(os.path.join(
                sublime.packages_path(), package, settings["tests_dir"]), settings["pattern"]
            )
            # use deferred test runner or default test runner
            if settings["deferred"]:
                testRunner = DeferringTextTestRunner(stream, verbosity=settings["verbosity"])
            else:
                testRunner = TextTestRunner(stream, verbosity=settings["verbosity"])

            testRunner.run(test)

        except Exception as e:
            if not stream.closed:
                stream.write("ERROR: %s\n" % e)

        self.cleanup_testing(testRunner, stream, stdout, stderr, handler, settings)

    def cleanup_testing(self, testRunner, stream, stdout, stderr, handler, settings):
        if not settings["deferred"] or (testRunner and testRunner.finished):
            stream.write("\nUnitTesting: Bye!\n")
            stream.close()

        if (not testRunner and settings["capture_console"]) or \
                (not settings["deferred"] or testRunner.finished):
            sys.stdout = stdout
            sys.stderr = stderr
            # remove stream set by logging.root.addHandler
            logging.root.removeHandler(handler)
        else:
            sublime.set_timeout(
                lambda: self.cleanup_testing(
                    testRunner, stream, stdout, stderr, handler, settings), 500)

    def syntax_testing(self, stream, package):
        total_assertions = 0
        failed_assertions = 0

        if version < "3103":
            stream.write("Warning: Syntax test is only avaliable on Sublime Text >3103.\n")
            stream.write("OK\n")
            stream.close()
            return

        try:
            tests = sublime.find_resources("syntax_test*")
            tests = [t for t in tests if t.startswith("Packages/%s/" % package)]
            if not tests:
                raise RuntimeError("No syntax_test files are found in %s!" % package)
            for t in tests:
                assertions, test_output_lines = sublime_api.run_syntax_test(t)
                total_assertions += assertions
                if len(test_output_lines) > 0:
                    failed_assertions += len(test_output_lines)
                    for line in test_output_lines:
                        stream.write(line + "\n")
            if failed_assertions > 0:
                stream.write("FAILED: %d of %d assertions in %d files failed\n" %
                             (failed_assertions, total_assertions, len(tests)))
            else:
                stream.write("Success: %d assertions in %s files passed\n" %
                             (total_assertions, len(tests)))
                stream.write("OK\n")
        except Exception as e:
            if not stream.closed:
                stream.write("ERROR: %s\n" % e)

        stream.close()
