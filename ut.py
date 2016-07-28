import sublime
import sys
import os

version = sublime.version()
platform = sublime.platform()

if version >= "3000":
    coverage_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "coverage",
        "st3_%s_%s" % (platform, sublime.arch())))

    if os.path.exists(coverage_path) and coverage_path not in sys.path:
        sys.path.append(coverage_path)

    from . import unittesting
    sys.modules["unittesting"] = unittesting


from unittesting import (
    UnitTestingRunSchedulerCommand,
    UnitTestingCommand,
    UnitTestingCoverageCommand,
    UnitTestingCurrentFileCommand,
    UnitTestingCurrentProjectCommand,
    UnitTestingCurrentProjectCoverageCommand,
    UnitTestingCurrentProjectReloadCommand,
    UnitTestingSyntaxCommand,
    OutputPanelInsertCommand,
    run_scheduler
)


def plugin_loaded():
    # run the schedule
    run_scheduler()

if version < "3000":
    plugin_loaded()
