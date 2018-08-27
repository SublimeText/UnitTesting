import os
import sublime
import sys

coverage_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "Packages",
    "coverage",
    "st3_%s_%s" % (sublime.platform(), sublime.arch())
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
