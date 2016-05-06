import sublime
import sys

version = sublime.version()

if version >= "3000":
    from .unittesting import (
        UnitTestingRunSchedulerCommand,
        UnitTestingCommand,
        OutputPanelInsertCommand,
        run_scheduler
    )
    sys.modules['unittesting'] = sys.modules['UnitTesting.unittesting']
else:
    from unittesting import (
        UnitTestingRunSchedulerCommand,
        UnitTestingCommand,
        OutputPanelInsertCommand,
        run_scheduler
    )

# run the schedule
run_scheduler()
