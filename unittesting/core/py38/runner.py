import sublime
import time
import warnings

from functools import partial
from unittest.runner import TextTestRunner
from unittest.runner import registerResult

DEFAULT_CONDITION_POLL_TIME = 17
DEFAULT_CONDITION_TIMEOUT = 4000
AWAIT_WORKER = "AWAIT_WORKER"
# Extract `set_timeout_async`, t.i. *avoid* late binding, in case a user
# patches it
run_on_worker = sublime.set_timeout_async


def defer(delay, callback, *args, **kwargs):
    # Rely on late binding in case a user patches it
    sublime.set_timeout(partial(callback, *args, **kwargs), delay)


class DeferringTextTestRunner(TextTestRunner):
    """This test runner runs tests in deferred slices."""

    def __init__(
        self,
        stream=None,
        descriptions=True,
        verbosity=1,
        failfast=False,
        buffer=False,
        resultclass=None,
        warnings=None,
        *,
        condition_timeout=DEFAULT_CONDITION_TIMEOUT,
        **kwargs
    ):
        super(DeferringTextTestRunner, self).__init__(
            stream,
            descriptions,
            verbosity,
            failfast,
            buffer,
            resultclass,
            warnings,
            **kwargs
        )
        self.condition_timeout = condition_timeout

    def run(self, test):
        """Run the given test case or test suite."""
        self.finished = False
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        result.tb_locals = self.tb_locals
        startTime = time.perf_counter()

        def _start_testing():
            with warnings.catch_warnings():
                if self.warnings:
                    # if self.warnings is set, use it to filter all the warnings
                    warnings.simplefilter(self.warnings)
                    # if the filter is 'default' or 'always', special-case the
                    # warnings from the deprecated unittest methods to show them
                    # no more than once per module, because they can be fairly
                    # noisy.  The -Wd and -Wa flags can be used to bypass this
                    # only when self.warnings is None.
                    if self.warnings in ["default", "always"]:
                        warnings.filterwarnings(
                            "module",
                            category=DeprecationWarning,
                            message=r"Please use assert\w+ instead.",
                        )
                startTestRun = getattr(result, "startTestRun", None)
                if startTestRun is not None:
                    startTestRun()
                try:
                    deferred = test(result)
                    _continue_testing(deferred)
                except Exception as e:
                    _handle_error(e)

        def _continue_testing(deferred, send_value=None, throw_value=None):
            try:
                if throw_value:
                    condition = deferred.throw(throw_value)
                else:
                    condition = deferred.send(send_value)

                if callable(condition):
                    defer(0, _wait_condition, deferred, condition)
                elif (
                    isinstance(condition, dict)
                    and "condition" in condition
                    and callable(condition["condition"])
                ):
                    period = condition.get("period", DEFAULT_CONDITION_POLL_TIME)
                    defer(period, _wait_condition, deferred, **condition)
                elif isinstance(condition, int):
                    defer(condition, _continue_testing, deferred)
                elif condition == AWAIT_WORKER:
                    run_on_worker(partial(defer, 0, _continue_testing, deferred))
                else:
                    defer(0, _continue_testing, deferred)

            except StopIteration:
                _stop_testing()

            except Exception as e:
                _handle_error(e)

        def _wait_condition(
            deferred,
            condition,
            period=DEFAULT_CONDITION_POLL_TIME,
            timeout=self.condition_timeout,
            start_time=None,
            timeout_message=None
        ):
            if start_time is None:
                start_time = time.time()

            try:
                send_value = condition()
            except Exception as e:
                _continue_testing(deferred, throw_value=e)
                return

            if send_value:
                _continue_testing(deferred, send_value=send_value)
            elif (time.time() - start_time) * 1000 >= timeout:
                if timeout_message is None:
                    timeout_message = "Condition not fulfilled"
                error = TimeoutError(
                    "{} within {:.2f} seconds".format(
                        timeout_message,
                        timeout / 1000
                    )
                )
                _continue_testing(deferred, throw_value=error)
            else:
                defer(
                    period,
                    _wait_condition,
                    deferred,
                    condition,
                    period,
                    timeout,
                    start_time,
                )

        def _handle_error(e):
            stopTestRun = getattr(result, "stopTestRun", None)
            if stopTestRun is not None:
                stopTestRun()
            self.finished = True
            raise e

        def _stop_testing():
            with warnings.catch_warnings():
                stopTestRun = getattr(result, "stopTestRun", None)
                if stopTestRun is not None:
                    stopTestRun()

            stopTime = time.perf_counter()
            timeTaken = stopTime - startTime
            result.printErrors()
            if hasattr(result, "separator2"):
                self.stream.writeln(result.separator2)
            run = result.testsRun
            self.stream.writeln(
                "Ran %d test%s in %.3fs" % (run, run != 1 and "s" or "", timeTaken)
            )
            self.stream.writeln()

            expectedFails = unexpectedSuccesses = skipped = 0
            try:
                results = map(
                    len,
                    (
                        result.expectedFailures,
                        result.unexpectedSuccesses,
                        result.skipped,
                    ),
                )
            except AttributeError:
                pass
            else:
                expectedFails, unexpectedSuccesses, skipped = results

            infos = []
            if not result.wasSuccessful():
                self.stream.write("FAILED")
                failed, errored = len(result.failures), len(result.errors)
                if failed:
                    infos.append("failures=%d" % failed)
                if errored:
                    infos.append("errors=%d" % errored)
            else:
                self.stream.write("OK")
            if skipped:
                infos.append("skipped=%d" % skipped)
            if expectedFails:
                infos.append("expected failures=%d" % expectedFails)
            if unexpectedSuccesses:
                infos.append("unexpected successes=%d" % unexpectedSuccesses)
            if infos:
                self.stream.writeln(" (%s)" % (", ".join(infos),))
            else:
                self.stream.write("\n")

            self.finished = True

        _start_testing()
