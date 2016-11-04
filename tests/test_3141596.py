import os
import re
import shutil
from functools import wraps
from unittest import TestCase
from unittesting.utils import UTSetting
from unittesting import DeferrableTestCase
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


def perpare_package(package, output=None, syntax_test=False, delay=None):
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

            if syntax_test:
                yield 1000
                sublime.run_command(
                    "unit_testing_syntax", {"package": package, "output": outfile})
            else:
                sublime.run_command(
                    "unit_testing", {"package": package, "output": outfile})

            if delay:
                yield delay
            with open(result_file, 'r') as f:
                txt = f.read()
            m = re.search('^UnitTesting: Done\\.', txt, re.MULTILINE)
            self.assertTrue(hasattr(m, "group"))
            func(self, txt)
            cleanup_package(package)
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

    @perpare_package("_Deferred", delay=2000)
    def test_deferred(self, txt):
        m = re.search('^OK', txt, re.MULTILINE)
        self.assertTrue(hasattr(m, "group"))
        yield 1000

    if version >= '3000':
        @perpare_package("_Async", delay=2000)
        def test_async(self, txt):
            m = re.search('^OK', txt, re.MULTILINE)
            self.assertTrue(hasattr(m, "group"))
            yield 1000


if version >= '3103':
    class TestSyntax(DeferrableTestCase):

        def tearDown(self):
            UTSetting.set("recent-package", "UnitTesting")

        @perpare_package("_Syntax_Failure", syntax_test=True)
        def test_fail_syntax(self, txt):
            m = re.search('^FAILED: 1 of 21 assertions in 1 files failed$', txt, re.MULTILINE)
            self.assertTrue(hasattr(m, "group"))

        @perpare_package("_Syntax_Success", syntax_test=True)
        def test_success_syntax(self, txt):
            m = re.search('^OK', txt, re.MULTILINE)
            self.assertTrue(hasattr(m, "group"))

        @perpare_package("_Syntax_Error", syntax_test=True)
        def test_error_syntax(self, txt):
            m = re.search('^ERROR: No syntax_test', txt, re.MULTILINE)
            self.assertTrue(hasattr(m, "group"))
