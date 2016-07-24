import sublime
import sublime_plugin
import sys
import os
import logging
import re
from unittest import TextTestRunner
from .core import TestLoader
from .core import DeferringTextTestRunner
from .mixin import UnitTestingMixin
from .const import DONE_MESSAGE

version = sublime.version()
platform = sublime.platform()

if version >= "3000" and platform != "windows":
    import coverage


class UnitTestingCommand(sublime_plugin.ApplicationCommand, UnitTestingMixin):

    def run(self, package=None, **kargs):

        if not package:
            self.prompt_package(lambda x: self.run(x, **kargs))
            return
        package, pattern = self.input_parser(package)
        settings = self.load_settings(package, pattern=pattern, **kargs)
        stream = self.load_stream(package, settings["output"])

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
        if settings["coverage"]:
            package_path = os.path.join(sublime.packages_path(), package)
            data_file = os.path.join(package_path, ".coverage")
            config_file = os.path.join(package_path, ".coveragerc")
            include = "{}/*".format(package_path)
            omit = "{}/{}/*".format(package_path, settings["tests_dir"])
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    txt = f.read()
                    if re.search("^include", txt, re.M):
                        include = None
                    if re.search("^omit", txt, re.M):
                        omit = None
            else:
                config_file = None
            cov = coverage.Coverage(
                data_file=data_file, config_file=config_file, include=include, omit=omit)
            cov.start()
        else:
            cov = None
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
            # force clean up
            testRunner = None
        finally:
            def clean_up(status=0):
                if not settings["deferred"] or not testRunner or \
                        testRunner.finished or status > 600:

                    if settings["coverage"]:
                        stream.write("\n")
                        cov.stop()
                        old_wd = os.getcwd()
                        os.chdir(package_path)
                        coverage.files.set_relative_directory()
                        cov.report(file=stream)
                        if settings["output"] != "<panel>":
                            cov.save()
                        os.chdir(old_wd)

                    stream.write("\n")
                    stream.write(DONE_MESSAGE)
                    stream.close()
                    if settings["capture_console"]:
                        sys.stdout = stdout
                        sys.stderr = stderr
                        # remove stream set by logging.root.addHandler
                        logging.root.removeHandler(handler)

                else:
                    sublime.set_timeout(lambda: clean_up(status+1), 500)

            clean_up()
