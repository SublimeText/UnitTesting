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
outputdir = os.path.join(
    sublime.packages_path(), 'User', 'UnitTesting', "tests_output")


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
        os.unlink(os.path.join(outputdir, package))
    except:
        pass


def cleanup_package(package):
    try:
        shutil.rmtree(os.path.join(sublime.packages_path(), package))
    except:
        pass


def perpare_package(package, output="<file>", syntax_test=False, defer=0):
    def wrapper(func):
        @wraps(func)
        def real_wrapper(self):
            set_package(package)
            if syntax_test:
                yield 1000
                sublime.run_command(
                    "unit_testing_syntax", {"package": package, "output": output})
            else:
                sublime.run_command(
                    "unit_testing_package", {"package": package, "output": output})
            if output == "<file>":
                with open(os.path.join(outputdir, package), 'r') as f:
                    txt = f.read()
            else:
                with open(os.path.join(sublime.packages_path(), package, output), 'r') as f:
                    txt = f.read()
            m = re.search('^UnitTesting: Done\\.', txt, re.MULTILINE)
            self.assertTrue(hasattr(m, "group"))
            func(self, txt)
            cleanup_package(package)
        return real_wrapper
    return wrapper


class TestUnitTesting(TestCase):

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


# sublime.run_command("unit_testing", ...) does not play well with DeferrableTestCase
# since DeferrableTestCase is non-blocking, we put the tests here instead
class TestDeferrable(DeferrableTestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()
        # make sure we have a window to work with
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def setText(self, string):
        self.view.run_command("insert", {"characters": string})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def test_defer(self):
        self.setText("foo")
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(0, 0))
        sublime.set_timeout(lambda: self.setText("foo"), 100)
        yield 200
        self.assertEqual(self.getRow(0), "foofoo")


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
