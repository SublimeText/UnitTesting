import sublime
import sublime_plugin
import sys
import os
import logging
from unittest import TextTestRunner, TestSuite
from .core import (
    TestLoader,
    DeferringTextTestRunner,
    DeferrableTestCase
)
from .mixin import UnitTestingMixin
from .const import DONE_MESSAGE
from .utils import ProgressBar, StdioSplitter
import threading


class UnitTestingCommand(sublime_plugin.ApplicationCommand, UnitTestingMixin):
    fallback33 = "unit_testing33"

    def run(self, package=None, **kwargs):
        if not package:
            self.prompt_package(lambda x: self.run(x, **kwargs))
            return

        package, pattern = self.input_parser(package)

        if sys.version_info >= (3, 8) and self.package_python_version(package) == "3.3":
            print("run unit_testing in python 3.3")
            kwargs["package"] = package
            sublime.set_timeout(lambda: sublime.run_command(self.fallback33, kwargs))
            return

        if pattern is not None:
            # kwargs have the highest precedence when evaluating the settings,
            # so we sure don't want to pass `None` down
            kwargs['pattern'] = pattern

        settings = self.load_unittesting_settings(package, kwargs)
        stream = self.load_stream(package, settings)

        if settings["async"]:
            threading.Thread(target=lambda: self.unit_testing(stream, package, settings)).start()
        else:
            self.unit_testing(stream, package, settings)

    def verify_testsuite(self, tests):
        for t in tests:
            if isinstance(t, TestSuite):
                self.verify_testsuite(t)
            if isinstance(t, DeferrableTestCase):
                raise Exception("DeferrableTestCase is used but `deferred` is `false`.")

    def unit_testing(self, stream, package, settings, cleanup_hooks=[]):
        if settings["capture_console"]:
            stdout = sys.stdout
            stderr = sys.stderr
            handler = logging.StreamHandler(stream)
            logging.root.addHandler(handler)

            sys.stdout = StdioSplitter(stdout, stream)
            sys.stderr = StdioSplitter(stderr, stream)

        testRunner = None
        progress_bar = ProgressBar("Testing %s" % package)
        progress_bar.start()

        try:
            # use custom loader which supports reloading modules
            self.remove_test_modules(package, settings["tests_dir"])
            loader = TestLoader(settings["deferred"])
            package_dir = os.path.join(sublime.packages_path(), package)
            start_dir = os.path.join(package_dir, settings["tests_dir"])
            if os.path.exists(os.path.join(start_dir, "__init__.py")):
                tests = loader.discover(start_dir, settings["pattern"], top_level_dir=package_dir)
            else:
                tests = loader.discover(start_dir, settings["pattern"])
            # use deferred test runner or default test runner
            if settings["deferred"]:
                if settings["legacy_runner"]:
                    raise Exception("`legacy_runner=True` is deprecated.")
                testRunner = DeferringTextTestRunner(
                    stream, verbosity=settings["verbosity"], failfast=settings['failfast'])
            else:
                self.verify_testsuite(tests)
                testRunner = TextTestRunner(stream, verbosity=settings["verbosity"], failfast=settings['failfast'])

            testRunner.run(tests)

        except Exception as e:
            if not stream.closed:
                import traceback
                stream.write("ERROR: %s\n" % e)
                traceback.print_exc(file=stream)
            # force clean up
            testRunner = None
        finally:
            def cleanup(status=0):
                if not settings["deferred"] or not testRunner or \
                        testRunner.finished or status > 600:
                    self.remove_test_modules(package, settings["tests_dir"])
                    progress_bar.stop()

                    for hook in cleanup_hooks:
                        try:
                            hook()
                        except Exception as e:
                            import traceback
                            stream.write("ERROR: %s\n" % e)
                            traceback.print_exc(file=stream)

                    if not hasattr(stream, 'window'):
                        # If it's an output panel don't print done message,
                        # because it's only required for CI test runs.
                        stream.write("\n")
                        stream.write(DONE_MESSAGE)

                    stream.close()

                    if settings["capture_console"]:
                        sys.stdout = stdout
                        sys.stderr = stderr
                        # remove stream set by logging.root.addHandler
                        logging.root.removeHandler(handler)
                else:
                    sublime.set_timeout(lambda: cleanup(status + 1), 500)

            cleanup()
