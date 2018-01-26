import os
import sublime
import sys
import shutil


if sys.version_info >= (3, 8):
    coverage_prefix = "st4"
else:
    coverage_prefix = "st3"

coverage_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "Packages",
    "coverage",
    "%s_%s_%s" % (coverage_prefix, sublime.platform(), sublime.arch())
))

if os.path.exists(coverage_path) and coverage_path not in sys.path:
    sys.path.append(coverage_path)

from . import unittesting  # noqa: F402
sys.modules["unittesting"] = unittesting

from unittesting import UnitTestingRunSchedulerCommand  # noqa: F401
from unittesting import UnitTestingCommand  # noqa: F401
from unittesting import UnitTestingCoverageCommand  # noqa: F401
from unittesting import UnitTestingCurrentFileCommand  # noqa: F401
from unittesting import UnitTestingCurrentFileCoverageCommand  # noqa: F401
from unittesting import UnitTestingCurrentPackageCommand  # noqa: F401
from unittesting import UnitTestingCurrentPackageCoverageCommand  # noqa: F401
from unittesting import UnitTestingSyntaxCommand  # noqa: F401
from unittesting import UnitTestingSyntaxCompatibilityCommand  # noqa: F401
from unittesting import UnitTestingColorSchemeCommand  # noqa: F401

from unittesting.commands import UnitTestingTestCancelCommand  # noqa: F401
from unittesting.commands import UnitTestingTestFileCommand  # noqa: F401
from unittesting.commands import UnitTestingTestLastCommand  # noqa: F401
from unittesting.commands import UnitTestingTestNearestCommand  # noqa: F401
from unittesting.commands import UnitTestingTestResultsCommand  # noqa: F401
from unittesting.commands import UnitTestingTestSuiteCommand  # noqa: F401
from unittesting.commands import UnitTestingTestSwitchCommand  # noqa: F401
from unittesting.commands import UnitTestingTestVisitCommand  # noqa: F401

__all__ = [
    "UnitTestingRunSchedulerCommand",
    "UnitTestingCommand",
    "UnitTestingCoverageCommand",
    "UnitTestingCurrentFileCommand",
    "UnitTestingCurrentFileCoverageCommand",
    "UnitTestingCurrentPackageCommand",
    "UnitTestingCurrentPackageCoverageCommand",
    "UnitTestingSyntaxCommand",
    "UnitTestingSyntaxCompatibilityCommand",
    "UnitTestingColorSchemeCommand",
    "UnitTestingTestCancelCommand",
    "UnitTestingTestFileCommand",
    "UnitTestingTestLastCommand",
    "UnitTestingTestNearestCommand",
    "UnitTestingTestResultsCommand",
    "UnitTestingTestSuiteCommand",
    "UnitTestingTestSwitchCommand",
    "UnitTestingTestVisitCommand"
]


def plugin_loaded():
    if sys.version_info >= (3, 8):
        UT33 = os.path.join(sublime.packages_path(), "UnitTesting33")
        if not os.path.exists(UT33):
            os.makedirs(UT33)
        data = sublime.load_resource("Packages/UnitTesting/py33/ut.py")
        with open(os.path.join(UT33, "ut.py"), 'w') as f:
            f.write(data.replace("\r\n", "\n"))
        with open(os.path.join(UT33, ".package_reloader.json"), 'w') as f:
            f.write("{\"dependencies\" : [\"UnitTesting\"]}")


def plugin_unloaded():
    if sys.version_info >= (3, 8):
        UT33 = os.path.join(sublime.packages_path(), "UnitTesting33")
        try:
            from AutomaticPackageReloader.package_reloader import reload_lock
            reloading = not reload_lock.acquire(blocking=False)
        except ImportError:
            reloading = False

        if os.path.exists(UT33) and not reloading:
            try:
                shutil.rmtree(UT33)
            except Exception:
                pass
