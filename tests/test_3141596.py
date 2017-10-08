import os
import re
import shutil
from functools import wraps
from unittesting.utils import UTSetting
from unittesting import DeferrableTestCase
from unittesting.helpers import TempDirectoryTestCase
import sublime

version = sublime.version()

__dir__ = os.path.dirname(os.path.abspath(__file__))
UUT_dir = os.path.join(
    sublime.packages_path(), 'User', 'UnitTesting')


def set_package(package):
    try:
        shutil.rmtree(os.path.join(sublime.packages_path(), package))
    except:
        pass
    try:
        shutil.copytree(
            os.path.join(__dir__, package),
            os.path.join(sublime.packages_path(), package))
    except:
        pass
    try:
        shutil.rmtree(os.path.join(UUT_dir, package))
    except:
        pass


def cleanup_package(package):
    try:
        shutil.rmtree(os.path.join(sublime.packages_path(), package))
    except:
        pass


def perpare_package(package, output=None, syntax_test=False, color_scheme_test=False, delay=None):
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
            m = re.search('^UnitTesting: Done\\.', txt, re.MULTILINE)
            self.assertTrue(hasattr(m, "group"))
            deferred = func(self, txt)
            if deferred is not None and hasattr(deferred, "__iter__"):
                for x in deferred:
                    yield x
            cleanup_package(package)
            if delay:
                yield 100
        return real_wrapper
    return wrapper


class TestUnitTesting(DeferrableTestCase):

    def tearDown(self):
        UTSetting.set("recent-package", "UnitTesting")

    @perpare_package("_Success")
    def test_success(self, txt):
        m = re.search('^OK', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))

    @perpare_package("_Failure")
    def test_failure(self, txt):
        m = re.search('^FAILED \(failures=1\)', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))

    @perpare_package("_Error")
    def test_error(self, txt):
        m = re.search('^ERROR', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))

    @perpare_package("_Output", "tests/result")
    def test_output(self, txt):
        m = re.search('^OK', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))

    @perpare_package("_Deferred", delay=3000)
    def test_deferred(self, txt):
        m = re.search('^OK', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))

    @perpare_package("_Async", delay=3000)
    def test_async(self, txt):
        m = re.search('^OK', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))


class TestSyntax(DeferrableTestCase):

    def tearDown(self):
        UTSetting.set("recent-package", "UnitTesting")

    @perpare_package("_Syntax_Failure", syntax_test=True, delay=1000)
    def test_fail_syntax(self, txt):
        m = re.search('^FAILED: 1 of 21 assertions in 1 files failed$', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))

    @perpare_package("_Syntax_Success", syntax_test=True, delay=1000)
    def test_success_syntax(self, txt):
        m = re.search('^OK', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))

    @perpare_package("_Syntax_Error", syntax_test=True, delay=1000)
    def test_error_syntax(self, txt):
        m = re.search('^ERROR: No syntax_test', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))


class TestColorScheme(DeferrableTestCase):

    def tearDown(self):
        UTSetting.set("recent-package", "UnitTesting")

    @perpare_package("_ColorScheme_Failure", color_scheme_test=True, delay=1000)
    def test_fail_color_scheme(self, txt):
        m = re.search('^There were 14 failures:$', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))

    @perpare_package("_ColorScheme_Success", color_scheme_test=True, delay=1000)
    def test_success_color_scheme(self, txt):
        m = re.search('^OK', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))


def tidy_path(path):
    return os.path.realpath(os.path.normcase(path))


class TestTempDirectoryTestCase(TempDirectoryTestCase):

    def test_temp_dir(self):
        self.assertTrue(tidy_path(
            self._temp_dir),
            tidy_path(self.window.folders()[0]))
