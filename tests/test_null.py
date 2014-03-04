import sublime
from unittest import TestCase
import os, re


outputdir = os.path.join(sublime.packages_path(), 'User', 'UnitTesting', "tests_output")

class TestNull(TestCase):

    def test_success(self):

        sublime.run_command("unit_testing", {"package":"Success"})
        with open(os.path.join(outputdir, "Success"), 'r') as f:
            txt = f.read()
        m = re.search('^OK',txt, re.MULTILINE)
        self.assertEqual(hasattr(m,"group"),True)

    def test_failure(self):

        sublime.run_command("unit_testing", {"package":"Failure"})
        with open(os.path.join(outputdir, "Failure"), 'r') as f:
            txt = f.read()
        m = re.search('^FAILED \(failures=1\)',txt, re.MULTILINE)
        self.assertEqual(hasattr(m,"group"),True)
