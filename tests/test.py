import os
import re
import shutil
from unittest import TestCase
from unittesting.utils import UTSetting
from unittesting import DeferrableTestCase
import sublime

version = sublime.version()

__dir__ = os.path.dirname(os.path.abspath(__file__))
outputdir = os.path.join(
    sublime.packages_path(), 'User', 'UnitTesting', "tests_output")


class TestUnitTesting(TestCase):

    def tearDown(self):
        UTSetting.set("recent-package", "UnitTesting")

    def test_success(self):
        try:
            shutil.copytree(
                os.path.join(__dir__, "_Success"),
                os.path.join(sublime.packages_path(), "_Success")
            )
        except:
            pass
        try:
            os.unlink(os.path.join(outputdir, "_Success"))
        except:
            pass
        sublime.run_command("unit_testing", {"package": "_Success", "output": "<file>"})
        with open(os.path.join(outputdir, "_Success"), 'r') as f:
            txt = f.read()
        m = re.search('^OK', txt, re.MULTILINE)
        shutil.rmtree(os.path.join(sublime.packages_path(), "_Success"))
        self.assertEqual(hasattr(m, "group"), True)

    def test_failure(self):
        try:
            shutil.copytree(
                os.path.join(__dir__, "_Failure"),
                os.path.join(sublime.packages_path(), "_Failure")
            )
        except:
            pass
        try:
            os.unlink(os.path.join(outputdir, "_Failure"))
        except:
            pass
        sublime.run_command("unit_testing", {"package": "_Failure", "output": "<file>"})
        with open(os.path.join(outputdir, "_Failure"), 'r') as f:
            txt = f.read()
        m = re.search('^FAILED \(failures=1\)', txt, re.MULTILINE)
        shutil.rmtree(os.path.join(sublime.packages_path(), "_Failure"))
        self.assertEqual(hasattr(m, "group"), True)

    def test_error(self):
        # Run unittesting for an non existing package
        try:
            os.unlink(os.path.join(outputdir, "_Error"))
        except:
            pass
        sublime.run_command("unit_testing", {"package": "_Error", "output": "<file>"})
        with open(os.path.join(outputdir, "_Error"), 'r') as f:
            txt = f.read()
        m = re.search('^ERROR', txt, re.MULTILINE)
        self.assertEqual(hasattr(m, "group"), True)

    def test_output(self):
        # Testing custom test output
        try:
            shutil.copytree(
                os.path.join(__dir__, "_Output"),
                os.path.join(sublime.packages_path(), "_Output")
            )
        except:
            pass
        try:
            os.unlink(os.path.join(sublime.packages_path(), "_Output", "tests", "result"))
        except:
            pass
        sublime.run_command("unit_testing", {"package": "_Output"})
        with open(os.path.join(sublime.packages_path(), "_Output", "tests", "result"), 'r') as f:
            txt = f.read()
        m = re.search('^OK', txt, re.MULTILINE)
        shutil.rmtree(os.path.join(sublime.packages_path(), "_Output"))
        self.assertEqual(hasattr(m, "group"), True)


if version >= '3000':
    class TestSyntax(DeferrableTestCase):

        def test_fail_syntax(self):
            # Testing custom test output
            try:
                shutil.copytree(
                    os.path.join(__dir__, "_Syntax"),
                    os.path.join(sublime.packages_path(), "_Syntax")
                )
            except:
                pass
            try:
                shutil.copyfile(os.path.join(sublime.packages_path(), "_Syntax", "fail.c++"),
                    os.path.join(sublime.packages_path(), "_Syntax", "syntax_test.c++"))
            except:
                pass
            yield 1000
            sublime.run_command("unit_testing", {
                "package": "_Syntax",
                "output": "<file>",
                "syntax_test": True})
            with open(os.path.join(outputdir, "_Syntax"), 'r') as f:
                txt = f.read()
            m = re.search('^FAILED: 1 of 21 assertions in 1 files failed', txt, re.MULTILINE)
            shutil.rmtree(os.path.join(sublime.packages_path(), "_Syntax"))
            self.assertEqual(hasattr(m, "group"), True)

        def test_success_syntax(self):
            # Testing custom test output
            try:
                shutil.copytree(
                    os.path.join(__dir__, "_Syntax"),
                    os.path.join(sublime.packages_path(), "_Syntax")
                )
            except:
                pass
            try:
                shutil.copyfile(
                    os.path.join(sublime.packages_path(), "_Syntax", "success.c++"),
                    os.path.join(sublime.packages_path(), "_Syntax", "syntax_test.c++"))
            except:
                pass
            yield 1000
            sublime.run_command("unit_testing", {
                "package": "_Syntax",
                "output": "<file>",
                "syntax_test": True})
            with open(os.path.join(outputdir, "_Syntax"), 'r') as f:
                txt = f.read()
            m = re.search('^OK', txt, re.MULTILINE)
            shutil.rmtree(os.path.join(sublime.packages_path(), "_Syntax"))
            self.assertEqual(hasattr(m, "group"), True)

        def test_error_syntax(self):
            # Testing custom test output
            try:
                shutil.copytree(
                    os.path.join(__dir__, "_Syntax"),
                    os.path.join(sublime.packages_path(), "_Syntax")
                )
            except:
                pass
            yield 1000
            sublime.run_command("unit_testing", {
                "package": "_Syntax",
                "output": "<file>",
                "syntax_test": True})
            with open(os.path.join(outputdir, "_Syntax"), 'r') as f:
                txt = f.read()
            m = re.search('^ERROR: No syntax_test', txt, re.MULTILINE)
            shutil.rmtree(os.path.join(sublime.packages_path(), "_Syntax"))
            self.assertEqual(hasattr(m, "group"), True)


class TestDeferrable(DeferrableTestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            if len(self.view.window().views()) > 1:
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
        yield 1000
        self.assertEqual(self.getRow(0), "foofoo")
