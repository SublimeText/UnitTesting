import logging
import os
import re
import sublime
import sys
import threading

from unittest import TestSuite
from unittest import TextTestRunner

from .base import BaseUnittestingCommand
from .base import DONE_MESSAGE
from .core import DeferrableTestCase
from .core import DeferrableTestLoader
from .core import DeferringTextTestRunner
from .utils import reload_package
from .utils import StdioSplitter

try:
    import coverage

    # ST4 does not ship `_sysconfigdata__darwin_darwin` module, required by
    # coverage 7.x on MacOS, which causes `sysconfig.add_paths()` to fail.
    # On other OSs it returns potentially unwanted paths outside of ST ecosystem.
    # Thus monkey patch it.
    try:
        import coverage.inorout

        def __add_third_party_paths(paths):
            """Return $data/Lib/pythonXY as 3rd-party path."""
            libs_path = os.path.join(
                os.path.dirname(sublime.packages_path()),
                "Lib",
                "python{}{}".format(sys.version_info.major, sys.version_info.minor),
            )
            paths.add(libs_path)

        coverage.inorout.add_third_party_paths = __add_third_party_paths
    except:
        pass
except Exception:
    coverage = False


class UnitTestingCommand(BaseUnittestingCommand):
    def run(self, package=None, **kwargs):
        # no package provided, prompt for input
        if not package:
            package = self.current_package_name() or ""
            view = self.window.show_input_panel(
                "Package:", package, lambda x: self.run(x, **kwargs), None, None
            )
            view.run_command("select_all")
            return

        # parse input of form `<package>:<pattern>`
        parts = package.split(":", 1)
        if len(parts) == 2:
            package, kwargs["pattern"] = parts

        # resolve real package name
        if package == "$package_name":
            package = self.current_package_name()
            if not package:
                sublime.error_message("Cannot determine package name.")
                return

        # redirect to python 3.3 if needed
        if sys.version_info >= (3, 8):
            try:
                version = sublime.load_resource(
                    "Packages/" + package + "/.python-version"
                ).strip()
            except FileNotFoundError:
                version = "3.3"

            if version == "3.3":
                kwargs["package"] = package
                self.window.run_command("unit_testing33", kwargs)
                return

        settings = self.load_unittesting_settings(package, kwargs)

        # resolve $file_name in pattern argument
        pattern = kwargs.get("pattern")
        if pattern == "$file_name":
            pattern = self.current_test_file(settings.parents["pattern"])
            if not pattern:
                sublime.error_message("Cannot determine test file name.")
                return

            kwargs["pattern"] = pattern

        stream = self.load_stream(package, settings)

        def run_tests():
            if settings["async"]:
                threading.Thread(
                    target=self.run_coverage, args=(package, stream, settings)
                ).start()
            else:
                self.run_coverage(package, stream, settings)

        if settings["reload_package_on_testing"]:
            reload_package(package, on_done=run_tests)
        else:
            run_tests()

    def run_coverage(self, package, stream, settings):
        if not coverage or not settings["coverage"]:
            if settings["coverage"]:
                stream.write("Warning: coverage cannot be loaded.\n\n")

            self.run_tests(stream, package, settings, [])
            return

        packages_path = sublime.packages_path()
        package_path = os.path.join(packages_path, package)
        data_file_dir = os.path.join(packages_path, "User", "UnitTesting", package)
        os.makedirs(data_file_dir, exist_ok=True)
        data_file = os.path.join(data_file_dir, "coverage")
        if os.path.exists(data_file):
            os.unlink(data_file)
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
            config_file = False

        cov = coverage.Coverage(
            data_file=data_file, config_file=config_file, include=include, omit=omit
        )

        cov.start()

        if settings["coverage_on_worker_thread"]:
            original_set_timeout_async = sublime.set_timeout_async

            def set_timeout_async(callback, *args, **kwargs):
                def _():
                    sys.settrace(threading._trace_hook)
                    callback()

                original_set_timeout_async(_, *args, **kwargs)

            sublime.set_timeout_async = set_timeout_async

        def cleanup():
            if settings["coverage_on_worker_thread"]:
                sublime.set_timeout_async = original_set_timeout_async

            stream.write("\n")
            cov.stop()
            coverage.files.RELATIVE_DIR = os.path.normcase(package_path + os.sep)
            ignore_errors = cov.get_option("report:ignore_errors")
            show_missing = cov.get_option("report:show_missing")
            cov.report(
                file=stream, ignore_errors=ignore_errors, show_missing=show_missing
            )

            if settings["generate_xml_report"]:
                xml_report_file = os.path.join(package_path, "coverage.xml")
                cov.xml_report(outfile=xml_report_file, ignore_errors=ignore_errors)

            if settings["generate_html_report"]:
                html_output_dir = os.path.join(package_path, "htmlcov")
                cov.html_report(directory=html_output_dir, ignore_errors=ignore_errors)

            cov.save()

        self.run_tests(stream, package, settings, [cleanup])

    def run_tests(self, stream, package, settings, cleanup_hooks=[]):
        if settings["capture_console"]:
            stdout = sys.stdout
            stderr = sys.stderr
            handler = logging.StreamHandler(stream)
            logging.root.addHandler(handler)

            sys.stdout = StdioSplitter(stdout, stream)
            sys.stderr = StdioSplitter(stderr, stream)

        if settings["async"]:
            stream.write(
                "#####\nasync runner is deprecated, consider using the DeferrableTestCase.\n#####\n\n"
            )
            # force deferred to False
            settings["deferred"] = False

        testRunner = None
        is_empty_test = False

        try:
            package_dir = os.path.join(sublime.packages_path(), package)
            if not os.path.isdir(package_dir):
                raise FileNotFoundError("{} does not exists.".format(package_dir))

            start_dir = os.path.join(package_dir, settings["tests_dir"])
            is_empty_test = not os.path.isdir(start_dir)
            if not is_empty_test:
                # use custom loader which supports reloading modules
                self.remove_test_modules(package, settings["tests_dir"])
                loader = DeferrableTestLoader(settings["deferred"])
                if os.path.exists(os.path.join(start_dir, "__init__.py")):
                    tests = loader.discover(
                        start_dir, settings["pattern"], top_level_dir=package_dir
                    )
                else:
                    tests = loader.discover(start_dir, settings["pattern"])
                # use deferred test runner or default test runner
                if settings["deferred"]:
                    testRunner = DeferringTextTestRunner(
                        stream=stream,
                        verbosity=settings["verbosity"],
                        failfast=settings["failfast"],
                        condition_timeout=settings["condition_timeout"],
                    )
                else:
                    self.verify_testsuite(tests)
                    testRunner = TextTestRunner(
                        stream,
                        verbosity=settings["verbosity"],
                        failfast=settings["failfast"],
                    )

                testRunner.run(tests)

        except Exception as e:
            if not stream.closed:
                import traceback

                stream.write("ERROR: %s\n" % e)
                traceback.print_exc(file=stream)
            # force clean up
            testRunner = None

        finally:

            def cleanup():
                if not settings["deferred"] or not testRunner or testRunner.finished:
                    self.remove_test_modules(package, settings["tests_dir"])

                    for hook in cleanup_hooks:
                        try:
                            hook()
                        except Exception as e:
                            import traceback

                            stream.write("ERROR: %s\n" % e)
                            traceback.print_exc(file=stream)

                    if is_empty_test:
                        stream.write("No tests are found.\n\nOK\n")

                    if not hasattr(stream, "window"):
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
                    sublime.set_timeout(lambda: cleanup(), 500)

            cleanup()

    def remove_test_modules(self, package, tests_dir):
        tests_dir = os.path.join(sublime.packages_path(), package, tests_dir)
        real_tests_dir = os.path.realpath(tests_dir)

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
            if os.path.realpath(mpath).startswith(real_tests_dir):
                del sys.modules[mname]

        # remove tests dir in sys.path
        if tests_dir in sys.path:
            sys.path.remove(tests_dir)
        elif real_tests_dir in sys.path:
            sys.path.remove(real_tests_dir)

    def verify_testsuite(self, tests):
        for t in tests:
            if isinstance(t, TestSuite):
                self.verify_testsuite(t)
            if isinstance(t, DeferrableTestCase):
                raise Exception("DeferrableTestCase is used but `deferred` is `false`.")
