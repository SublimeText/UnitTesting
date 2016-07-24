import sublime
import sublime_plugin
import sys
import os
import logging
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
            settings.update({
                "converage_result": os.path.join(package_path, ".coverage")
            })
            config_file = os.path.join(package_path, ".coveragerc")
            cov = coverage.Coverage(
                config_file=config_file if os.path.exists(config_file) else None,
                include="{}/*".format(package_path))
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

        self.clean_up(testRunner, stream, stdout, stderr, handler, settings, cov)

    def clean_up(self, testRunner, stream, stdout, stderr, handler, settings, cov):
        if not settings["deferred"] or not testRunner or testRunner.finished:
            if settings["coverage"]:
                stream.write("\n")
                cov.stop()
                cov.report(ignore_errors=True, file=stream)
                cov.get_data().write_file(settings["converage_result"])
            stream.write("\n")
            stream.write(DONE_MESSAGE)
            stream.close()
            if settings["capture_console"]:
                sys.stdout = stdout
                sys.stderr = stderr
                # remove stream set by logging.root.addHandler
                logging.root.removeHandler(handler)

        else:
            sublime.set_timeout(
                lambda: self.clean_up(
                    testRunner, stream, stdout, stderr, handler, settings, cov), 500)
