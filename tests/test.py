import os
import re
import shutil
from unittest import TestCase

import sublime

version = sublime.version()

if version >= '3000':
    from UnitTesting.utils import recent as recent_package
else:
    from utils import recent as recent_package

__dir__ = os.path.dirname(os.path.abspath(__file__))
outputdir = os.path.join(
    sublime.packages_path(), 'User', 'UnitTesting', "tests_output")


class TestUnitTesting(TestCase):

    def tearDown(self):
        recently_used_file = "UnitTesting.recent-package"
        recently_used = sublime.load_settings(recently_used_file)
        recently_used.set("recent_package", "UnitTesting")
        sublime.save_settings(recently_used_file)

    def test_success(self):
        try:
            shutil.copytree(
                os.path.join(__dir__, "_Success"),
                os.path.join(sublime.packages_path(), "_Success")
            )
        except:
            pass
        sublime.run_command("unit_testing", {"package": "_Success"})
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
        sublime.run_command("unit_testing", {"package": "_Failure"})
        with open(os.path.join(outputdir, "_Failure"), 'r') as f:
            txt = f.read()
        m = re.search('^FAILED \(failures=1\)', txt, re.MULTILINE)
        shutil.rmtree(os.path.join(sublime.packages_path(), "_Failure"))
        self.assertEqual(hasattr(m, "group"), True)

    def test_error(self):
        # Run unittesting for an non existing package
        sublime.run_command("unit_testing", {"package": "_Error"})
        with open(os.path.join(outputdir, "_Error"), 'r') as f:
            txt = f.read()
        m = re.search('^ERROR', txt, re.MULTILINE)
        self.assertEqual(hasattr(m, "group"), True)
