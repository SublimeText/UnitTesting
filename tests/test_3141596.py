import os
import re
import shutil
import sublime

from functools import wraps
from unittest import skipIf
from unittesting import AWAIT_WORKER
from unittesting import DeferrableMethod
from unittesting import DeferrableTestCase

BASEDIR = os.path.dirname(os.path.abspath(__file__))


def setup_package(package):
    packages_path = sublime.packages_path()
    package_path = os.path.join(packages_path, package)
    try:
        shutil.rmtree(package_path)
    except FileNotFoundError:
        pass
    try:
        shutil.copytree(os.path.join(BASEDIR, package), package_path)
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree(os.path.join(packages_path, "User", "UnitTesting", package))
    except FileNotFoundError:
        pass


def cleanup_package(package):
    try:
        shutil.rmtree(os.path.join(sublime.packages_path(), package))
    except FileNotFoundError:
        pass


def with_package(package, output=None, syntax_test=False, syntax_compatibility=False,
                 color_scheme_test=False, wait_timeout=5000):
    def wrapper(func):
        @wraps(func)
        def real_wrapper(self):
            packages_path = sublime.packages_path()

            if output:
                # set by _Output/unittesting.json
                outfile = None
                result_file = os.path.join(packages_path, package, output)
            else:
                outfile = os.path.join(packages_path, "User", "UnitTesting", package, "result")
                result_file = outfile

            yield AWAIT_WORKER

            kwargs = {"package": package}
            if outfile:
                # Command kwargs have the highest precedence. Passing down
                # 'None' is not what we want, the intention is to omit it
                # so that the value from 'unittesting.json' wins.
                kwargs["output"] = outfile

            if syntax_test:
                sublime.run_command("unit_testing_syntax", kwargs)
            elif syntax_compatibility:
                sublime.run_command("unit_testing_syntax_compatibility", kwargs)
            elif color_scheme_test:
                sublime.run_command("unit_testing_color_scheme", kwargs)
            else:
                sublime.run_command("unit_testing", kwargs)

            def condition():
                try:
                    with open(result_file, 'r') as f:
                        txt = f.read()
                    return "UnitTesting: Done." in txt
                except FileNotFoundError:
                    return False

            yield {"condition": condition, "period": 200, "timeout": wait_timeout}

            with open(result_file, 'r') as f:
                txt = f.read()

            deferred = func(self, txt)
            if isinstance(deferred, DeferrableMethod):
                yield from deferred

            yield

        return real_wrapper

    return wrapper


class UnitTestingTestCase(DeferrableTestCase):
    fixtures = ()

    def setUp(self):
        for fixture in self.fixtures:
            setup_package(fixture)
        yield 500

    def tearDown(self):
        for fixture in self.fixtures:
            cleanup_package(fixture)

    def assertRegexContains(self, txt, expr, msg=None):
        if re.search(expr, txt, re.MULTILINE) is None:
            self.fail("String {!r} does not contain regexp {!r}.".format(
                txt, expr
            ))

    def assertOk(self, txt, msg=None):
        self.assertRegexContains(txt, r'^OK', msg)


class TestUnitTesting(UnitTestingTestCase):
    fixtures = (
        "_Success", "_Failure", "_Empty", "_Output", "_Deferred", "_Async"
    )

    @with_package("_Success")
    def test_success(self, txt):
        self.assertOk(txt)

    @with_package("_Failure")
    def test_failure(self, txt):
        self.assertRegexContains(txt, r'^FAILED \(failures=1\)')

    @with_package("_Error")
    def test_error(self, txt):
        self.assertRegexContains(txt, r'^ERROR')

    @with_package("_Empty")
    def test_empty(self, txt):
        self.assertRegexContains(txt, r'^No tests are found.')

    @with_package("_Output", "tests/result")
    def test_output(self, txt):
        self.assertOk(txt)

    @with_package("_Deferred")
    def test_deferred(self, txt):
        self.assertOk(txt)

    @with_package("_Async")
    def test_async(self, txt):
        self.assertOk(txt)


class TestSyntax(UnitTestingTestCase):
    fixtures = (
        "_Syntax_Failure",
        "_Syntax_Success",
        "_Syntax_Compat_Failure",
        "_Syntax_Compat_Success",
    )

    @with_package("_Syntax_Failure", syntax_test=True)
    def test_fail_syntax(self, txt):
        self.assertRegexContains(txt, r'^FAILED: 1 of 21 assertions in 1 file failed$')

    @with_package("_Syntax_Success", syntax_test=True)
    def test_success_syntax(self, txt):
        self.assertOk(txt)

    @with_package("_Syntax_Error", syntax_test=True)
    def test_error_syntax(self, txt):
        self.assertRegexContains(txt, r'^ERROR: No syntax_test')

    @with_package("_Syntax_Compat_Failure", syntax_compatibility=True)
    def test_fail_syntax_compatibility(self, txt):
        self.assertRegexContains(txt, r'^FAILED: 3 errors in 1 of 1 syntax$')

    @with_package("_Syntax_Compat_Success", syntax_compatibility=True)
    def test_success_syntax_compatibility(self, txt):
        self.assertOk(txt)


def has_colorschemeunit():
    return (
        os.path.isfile(os.path.join(sublime.installed_packages_path(), "ColorSchemeUnit.sublime-package")) or
        os.path.isdir(os.path.join(sublime.packages_path(), "ColorSchemeUnit"))
    )


class TestColorScheme(UnitTestingTestCase):
    fixtures = ("_ColorScheme_Failure", "_ColorScheme_Success")

    @skipIf(not has_colorschemeunit(), "ColorSchemeUnit is not installed")
    @with_package("_ColorScheme_Failure", color_scheme_test=True)
    def test_fail_color_scheme(self, txt):
        self.assertRegexContains(txt, r'^There were 14 failures:$')

    @skipIf(not has_colorschemeunit(), "ColorSchemeUnit is not installed")
    @with_package("_ColorScheme_Success", color_scheme_test=True)
    def test_success_color_scheme(self, txt):
        self.assertOk(txt)
