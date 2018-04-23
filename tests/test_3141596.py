import os
import re
import shutil
from functools import wraps
from unittesting.utils import isiterable
from unittesting import DeferrableTestCase
from unittesting.helpers import TempDirectoryTestCase
from unittesting.helpers import ViewTestCase
import sublime

__dir__ = os.path.dirname(os.path.abspath(__file__))
UUT_dir = os.path.join(
    sublime.packages_path(), 'User', 'UnitTesting')


def set_package(package):
    try:
        shutil.rmtree(os.path.join(sublime.packages_path(), package))
    except Exception:
        pass
    try:
        shutil.copytree(
            os.path.join(__dir__, package),
            os.path.join(sublime.packages_path(), package))
    except Exception:
        pass
    try:
        shutil.rmtree(os.path.join(UUT_dir, package))
    except Exception:
        pass


def cleanup_package(package):
    try:
        shutil.rmtree(os.path.join(sublime.packages_path(), package))
    except Exception:
        pass


def prepare_package(package, output=None, syntax_test=False, color_scheme_test=False, delay=None):
    def wrapper(func):
        @wraps(func)
        def real_wrapper(self):
            set_package(package)
            if output:
                # set by _Ooutput/unittesting.json
                outfile = None
                result_file = os.path.join(sublime.packages_path(), package, output)
            else:
                outfiledir = os.path.join(UUT_dir, package)
                outfile = os.path.join(outfiledir, "result")
                result_file = outfile
                if not os.path.isdir(outfiledir):
                    os.makedirs(outfiledir)

            if delay:
                yield delay

            if syntax_test:
                sublime.run_command(
                    "unit_testing_syntax", {"package": package, "output": outfile})
            elif color_scheme_test:
                sublime.run_command(
                    "unit_testing_color_scheme", {"package": package, "output": outfile})
            else:
                sublime.run_command(
                    "unit_testing", {"package": package, "output": outfile})

            if delay:
                yield delay

            with open(result_file, 'r') as f:
                txt = f.read()
            self.assertRegexContains(txt, r'^UnitTesting: Done\.')

            deferred = func(self, txt)
            if isiterable(deferred):
                yield from deferred

            cleanup_package(package)

            if delay:
                yield 100
        return real_wrapper
    return wrapper


class UnitTestingTestCase(DeferrableTestCase):

    def assertRegexContains(self, txt, expr, msg=None):
        m = re.search(expr, txt, re.MULTILINE)
        self.assertIsNotNone(m, msg)

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

    @prepare_package("_Deferred", delay=3000)
    def test_deferred(self, txt):
        self.assertOk(txt)

    @prepare_package("_Async", delay=3000)
    def test_async(self, txt):
        self.assertOk(txt)


class TestSyntax(UnitTestingTestCase):

    @prepare_package("_Syntax_Failure", syntax_test=True, delay=1000)
    def test_fail_syntax(self, txt):
        self.assertRegexContains(txt, r'^FAILED: 1 of 21 assertions in 1 files failed$')

    @prepare_package("_Syntax_Success", syntax_test=True, delay=1000)
    def test_success_syntax(self, txt):
        self.assertOk(txt)

    @prepare_package("_Syntax_Error", syntax_test=True, delay=1000)
    def test_error_syntax(self, txt):
        self.assertRegexContains(txt, r'^ERROR: No syntax_test')


class TestColorScheme(UnitTestingTestCase):

    @prepare_package("_ColorScheme_Failure", color_scheme_test=True, delay=1000)
    def test_fail_color_scheme(self, txt):
        self.assertRegexContains(txt, r'^There were 14 failures:$')

    @prepare_package("_ColorScheme_Success", color_scheme_test=True, delay=1000)
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
