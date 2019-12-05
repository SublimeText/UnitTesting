import os
import re
import shutil
from functools import wraps
from unittest import skipIf
from unittesting.utils import isiterable
from unittesting import DeferrableTestCase
from unittesting.helpers import TempDirectoryTestCase
from unittesting.helpers import ViewTestCase
from unittesting import AWAIT_WORKER
import sublime

BASEDIR = os.path.dirname(os.path.abspath(__file__))
UUTDIR = os.path.join(
    sublime.packages_path(), 'User', 'UnitTesting')


def set_package(package):
    try:
        shutil.rmtree(os.path.join(sublime.packages_path(), package))
    except Exception:
        pass
    try:
        shutil.copytree(
            os.path.join(BASEDIR, package),
            os.path.join(sublime.packages_path(), package))
    except Exception:
        pass
    try:
        shutil.rmtree(os.path.join(UUTDIR, package))
    except Exception:
        pass


def cleanup_package(package):
    try:
        shutil.rmtree(os.path.join(sublime.packages_path(), package))
    except Exception:
        pass


def prepare_package(package, output=None, syntax_test=False, syntax_compatibility=False,
                    color_scheme_test=False, delay=200, wait_timeout=5000):
    def wrapper(func):
        @wraps(func)
        def real_wrapper(self):
            set_package(package)
            if output:
                # set by _Ooutput/unittesting.json
                outfile = None
                result_file = os.path.join(sublime.packages_path(), package, output)
            else:
                outfiledir = os.path.join(UUTDIR, package)
                outfile = os.path.join(outfiledir, "result")
                result_file = outfile
                if not os.path.isdir(outfiledir):
                    os.makedirs(outfiledir)

            yield delay
            yield AWAIT_WORKER

            if syntax_test:
                sublime.run_command(
                    "unit_testing_syntax", {"package": package, "output": outfile})
            elif syntax_compatibility:
                sublime.run_command(
                    "unit_testing_syntax_compatibility", {"package": package, "output": outfile})
            elif color_scheme_test:
                sublime.run_command(
                    "unit_testing_color_scheme", {"package": package, "output": outfile})
            else:
                args = {"package": package}
                if outfile:
                    # Command args have the highest precedence. Passing down
                    # 'None' is not what we want, the intention is to omit it
                    # so that the value from 'unittesting.json' wins.
                    args["output"] = outfile
                sublime.run_command("unit_testing", args)

            def condition():
                with open(result_file, 'r') as f:
                    txt = f.read()
                return "UnitTesting: Done." in txt

            yield {"condition": condition, "timeout": 5000}

            with open(result_file, 'r') as f:
                txt = f.read()
            deferred = func(self, txt)
            if isiterable(deferred):
                yield from deferred

            cleanup_package(package)

            yield
        return real_wrapper
    return wrapper


class UnitTestingTestCase(DeferrableTestCase):

    def assertRegexContains(self, txt, expr, msg=None):
        if re.search(expr, txt, re.MULTILINE) is None:
            self.fail("String {!r} does not contain regexp {!r}.".format(
                txt, expr
            ))

    def assertOk(self, txt, msg=None):
        self.assertRegexContains(txt, r'^OK', msg)


class TestUnitTesting(UnitTestingTestCase):

    @prepare_package("_Success")
    def test_success(self, txt):
        self.assertOk(txt)

    @prepare_package("_Failure")
    def test_failure(self, txt):
        self.assertRegexContains(txt, r'^FAILED \(failures=1\)')

    @prepare_package("_Error")
    def test_error(self, txt):
        self.assertRegexContains(txt, r'^ERROR')

    @prepare_package("_Output", "tests/result")
    def test_output(self, txt):
        self.assertOk(txt)

    @prepare_package("_Deferred")
    def test_deferred(self, txt):
        self.assertOk(txt)

    @prepare_package("_Async")
    def test_async(self, txt):
        self.assertOk(txt)


class TestSyntax(UnitTestingTestCase):

    @prepare_package("_Syntax_Failure", syntax_test=True)
    def test_fail_syntax(self, txt):
        self.assertRegexContains(txt, r'^FAILED: 1 of 21 assertions in 1 files failed$')

    @prepare_package("_Syntax_Success", syntax_test=True)
    def test_success_syntax(self, txt):
        self.assertOk(txt)

    @prepare_package("_Syntax_Error", syntax_test=True)
    def test_error_syntax(self, txt):
        self.assertRegexContains(txt, r'^ERROR: No syntax_test')

    @prepare_package("_Syntax_Compat_Failure", syntax_compatibility=True)
    def test_fail_syntax_compatibility(self, txt):
        self.assertRegexContains(txt, r'^FAILED: 3 errors in 1 of 1 syntaxes$')

    @prepare_package("_Syntax_Compat_Success", syntax_compatibility=True)
    def test_success_syntax_compatibility(self, txt):
        self.assertOk(txt)


def has_colorschemeunit():
    if "ColorSchemeUnit.sublime-package" in os.listdir(sublime.installed_packages_path()):
        return True
    elif "ColorSchemeUnit" in os.listdir(sublime.packages_path()):
        return True
    return False


class TestColorScheme(UnitTestingTestCase):
    @skipIf(not has_colorschemeunit(), "ColorSchemeUnit is not installed")
    @prepare_package("_ColorScheme_Failure", color_scheme_test=True)
    def test_fail_color_scheme(self, txt):
        self.assertRegexContains(txt, r'^There were 14 failures:$')

    @skipIf(not has_colorschemeunit(), "ColorSchemeUnit is not installed")
    @prepare_package("_ColorScheme_Success", color_scheme_test=True)
    def test_success_color_scheme(self, txt):
        self.assertOk(txt)


def tidy_path(path):
    return os.path.realpath(os.path.normcase(path))


class TestTempDirectoryTestCase(TempDirectoryTestCase):

    def test_temp_dir(self):
        self.assertTrue(tidy_path(
            self._temp_dir),
            tidy_path(self.window.folders()[0]))


class TestViewTestCase(ViewTestCase):

    def test_view(self):
        self.assertIsInstance(self.view, sublime.View)
        self.assertTrue(self.view.is_valid())
