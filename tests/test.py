import os
import re
import shutil
from unittest import TestCase

import sublime

version = sublime.version()

if version >= '3000':
    from UnitTesting.utils import settings as plugin_settings
else:
    from utils import settings as plugin_settings

__dir__ = os.path.dirname(os.path.abspath(__file__))
outputdir = os.path.join(
    sublime.packages_path(), 'User', 'UnitTesting', "tests_output")


class TestUnitTesting(TestCase):

    def tearDown(self):
        plugin_settings.set("recent-package", "UnitTesting")

    def test_success(self):
        try:
            shutil.copytree(
                os.path.join(__dir__, "_Success"),
                os.path.join(sublime.packages_path(), "_Success")
            )
        except:
            pass
        os.unlink(os.path.join(outputdir, "_Success"))
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
        os.unlink(os.path.join(outputdir, "_Failure"))
        sublime.run_command("unit_testing", {"package": "_Failure"})
        with open(os.path.join(outputdir, "_Failure"), 'r') as f:
            txt = f.read()
        m = re.search('^FAILED \(failures=1\)', txt, re.MULTILINE)
        shutil.rmtree(os.path.join(sublime.packages_path(), "_Failure"))
        self.assertEqual(hasattr(m, "group"), True)

    def test_error(self):
        # Run unittesting for an non existing package
        os.unlink(os.path.join(outputdir, "_Error"))
        sublime.run_command("unit_testing", {"package": "_Error"})
        with open(os.path.join(outputdir, "_Error"), 'r') as f:
            txt = f.read()
        m = re.search('^ERROR', txt, re.MULTILINE)
        self.assertEqual(hasattr(m, "group"), True)
