import os
import re

import sublime
import sublime_plugin

version = sublime.version()

from unittest import TextTestRunner
from ..core import TestLoader
from ..core import DeferringTextTestRunner
from ..utils import UTSetting
from ..utils import OutputPanel
from ..utils import JsonFile


def input_parser(package):
    m = re.match(r'([^:]+):(.+)', package)
    if m:
        return m.groups()
    else:
        return (package, "test*.py")


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

    def run(self, package=None, output=None):

        if package:
            if package == "<current>":
                package = self.project_name
            if package:
                UTSetting.set("recent-package", package)
            else:
                sublime.message_dialog("Cannot find current package.")
                return

            package, pattern = input_parser(package)

            jfile = os.path.join(sublime.packages_path(), package, "unittesting.json")
            if os.path.exists(jfile):
                ss = JsonFile(jfile).load()
                tests_dir = ss.get("tests_dir", "tests")
                async = ss.get("async", False)
                deferred = ss.get("deferred", False)
                verbosity = ss.get("verbosity", 2)
            else:
                tests_dir, async, deferred, verbosity = "tests", False, False, 2

            if version < '3000':
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
                    lambda: self.testing(
                        package, tests_dir, pattern, stream, False, verbosity
                    ), 100)
            else:
                self.testing(package, tests_dir, pattern, stream, deferred, verbosity)

        else:
            # bootstrap run() with package input
            package = UTSetting.get("recent-package", "Package Name")
            if package:
                view = sublime.active_window().show_input_panel(
                    'Package:', package,
                    lambda x: sublime.run_command(
                        "unit_testing", {
                            "package": x,
                            "output": output
                        }), None, None
                    )
                view.run_command("select_all")

    def testing(self, package, tests_dir, pattern, stream, deferred=False, verbosity=2):
        try:
            # use custom loader which support ST2 and reloading modules
            loader = TestLoader(deferred)
            test = loader.discover(os.path.join(
                sublime.packages_path(), package, tests_dir), pattern
            )
            # use deferred test runner or default test runner
            if deferred:
                testRunner = DeferringTextTestRunner(stream, verbosity=verbosity)
            else:
                testRunner = TextTestRunner(stream, verbosity=verbosity)
            testRunner.run(test)
        except Exception as e:
            if not stream.closed:
                stream.write("ERROR: %s\n" % e)
        if not deferred:
            stream.close()
