import os
import sublime
import sys
import shutil

# Clear module cache to force reloading all modules of this package.

# kiss-reloader:
prefix = __package__ + "."  # don't clear the base package
for module_name in [
    module_name
    for module_name in sys.modules
    if module_name.startswith(prefix) and module_name != __name__
]:
    del sys.modules[module_name]
prefix = None

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
from unittesting import UnitTestingCurrentPackageCommand  # noqa: F401
from unittesting import UnitTestingCurrentPackageCoverageCommand  # noqa: F401
from unittesting import UnitTestingSyntaxCommand  # noqa: F401
from unittesting import UnitTestingSyntaxCompatibilityCommand  # noqa: F401
from unittesting import UnitTestingColorSchemeCommand  # noqa: F401


__all__ = [
    "UnitTestingRunSchedulerCommand",
    "UnitTestingCommand",
    "UnitTestingCoverageCommand",
    "UnitTestingCurrentFileCommand",
    "UnitTestingCurrentPackageCommand",
    "UnitTestingCurrentPackageCoverageCommand",
    "UnitTestingSyntaxCommand",
    "UnitTestingSyntaxCompatibilityCommand",
    "UnitTestingColorSchemeCommand"
]

UT33_CODE = """
from UnitTesting import ut as ut38  # noqa


class UnitTesting33Command(ut38.UnitTestingCommand):
    pass


class UnitTesting33CoverageCommand(ut38.UnitTestingCoverageCommand):
    pass


class UnitTesting33CurrentPackageCommand(ut38.UnitTestingCurrentPackageCommand):
    pass


class UnitTesting33CurrentPackageCoverageCommand(ut38.UnitTestingCurrentPackageCoverageCommand):
    pass


class UnitTesting33CurrentFileCommand(ut38.UnitTestingCurrentFileCommand):
    pass


class UnitTesting33ColorSchemeCommand(ut38.UnitTestingColorSchemeCommand):
    pass
"""


def plugin_loaded():
    if sys.version_info >= (3, 8):
        import json

        UT33 = os.path.join(sublime.packages_path(), "UnitTesting33")
        os.makedirs(UT33, exist_ok=True)

        try:
            try:
                with open(os.path.join(UT33, "ut.py"), 'x') as f:
                    f.write(UT33_CODE)
            except FileExistsError:
                pass

            try:
                with open(os.path.join(UT33, "dependencies.json"), 'x') as f:
                    f.write(json.dumps({"*": {">3000": ["coverage"]}}))
            except FileExistsError:
                pass

        except OSError as e:
            print("UnitTesting: Error while creating python 3.3 module, since", str(e))


def plugin_unloaded():
    if sys.version_info >= (3, 8):
        UT33 = os.path.join(sublime.packages_path(), "UnitTesting33")
        try:
            shutil.rmtree(UT33)
        except Exception:
            pass
