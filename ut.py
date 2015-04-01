import sublime

version = sublime.version()

if version >= "3000":
    from .unittesting import (
        deferred_run,
        UnitTestingRunSchedulerCommand,
        UnitTestingCommand,
        OutputPanelInsertCommand
    )
else:
    from unittesting import (
        deferred_run,
        UnitTestingRunSchedulerCommand,
        UnitTestingCommand,
        OutputPanelInsertCommand
    )
# run the schedule using deferred_run, it will ensure all packages are loaded
deferred_run("unit_testing_run_scheduler")
