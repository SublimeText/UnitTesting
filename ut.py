import sublime
import sys
import os

version = sublime.version()
platform = sublime.platform()

if version >= "3000":
    if platform != "windows":
        coverage_path = os.path.join(os.path.dirname(__file__), "vendor")
        if coverage_path not in sys.path:
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
