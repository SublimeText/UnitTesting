import sublime
import sys

version = sublime.version()

if version >= "3000":
    import UnitTesting.unittesting
    sys.modules['unittesting'] = sys.modules['UnitTesting.unittesting']


from unittesting import (
    UnitTestingRunSchedulerCommand,
    UnitTestingCommand,
    UnitTestingCurrentFileCommand,
    UnitTestingCurrentProjectCommand,
    UnitTestingSyntaxCommand,
    OutputPanelInsertCommand,
    run_scheduler
)

# run the schedule
run_scheduler()
