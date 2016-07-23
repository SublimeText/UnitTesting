import sublime
import sublime_plugin
import sys
import os
import logging
from unittest import TextTestRunner
from .core import TestLoader
from .core import DeferringTextTestRunner
from .mixin import UnitTestingMixin
from .const import BYE_STRING

version = sublime.version()


class UnitTestingCommand(sublime_plugin.ApplicationCommand, UnitTestingMixin):

    def run(self, package=None, output=None):

        if not package:
            self.prompt_package(lambda x: self.run(x, output))
            return
        package, pattern = self.input_parser(package)
        settings = self.load_settings(package, pattern, output)
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

        self.clean_up(testRunner, stream, stdout, stderr, handler, settings)

    def clean_up(self, testRunner, stream, stdout, stderr, handler, settings):
        if not settings["deferred"] or not testRunner or testRunner.finished:
            stream.write("\n")
            stream.write(BYE_STRING)
            stream.close()
            if settings["capture_console"]:
                sys.stdout = stdout
                sys.stderr = stderr
                # remove stream set by logging.root.addHandler
                logging.root.removeHandler(handler)
        else:
            sublime.set_timeout(
                lambda: self.clean_up(
                    testRunner, stream, stdout, stderr, handler, settings), 500)
