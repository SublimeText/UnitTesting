import time
from unittest.runner import TextTestRunner, registerResult
import warnings
import sublime


def defer(delay, callback, *args, **kwargs):
    sublime.set_timeout(lambda: callback(*args, **kwargs), delay)


class DeferringTextTestRunner(TextTestRunner):
    """This test runner runs tests in deferred slices."""

    def run(self, test):
        """Run the given test case or test suite."""
        self.finished = False
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        startTime = time.time()

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
                    if self.warnings in ['default', 'always']:
                        warnings.filterwarnings(
                            'module',
                            category=DeprecationWarning,
                            message='Please use assert\w+ instead.')
                startTestRun = getattr(result, 'startTestRun', None)
                if startTestRun is not None:
                    startTestRun()
                try:
                    deferred = test(result)
                    defer(10, _continue_testing, deferred)

                except Exception as e:
                    _handle_error(e)

        def _continue_testing(deferred):
            try:
                condition = next(deferred)
                if callable(condition):
                    defer(100, _wait_condition, deferred, condition)
                elif isinstance(condition, dict) and "condition" in condition and \
                        callable(condition["condition"]):
                    period = condition.get("period", 100)
                    defer(period, _wait_condition, deferred, **condition)
                elif isinstance(condition, int):
                    defer(condition, _continue_testing, deferred)
                else:
                    defer(10, _continue_testing, deferred)

            except StopIteration:
                _stop_testing()
                self.finished = True

            except Exception as e:
                _handle_error(e)

        def _wait_condition(deferred, condition, period=100, timeout=10000, start_time=None):
            if start_time is None:
                start_time = time.time()

            if condition():
                defer(10, _continue_testing, deferred)
            elif (time.time() - start_time) * 1000 >= timeout:
                self.stream.writeln("Condition timeout, continue anyway.")
                defer(10, _continue_testing, deferred)
            else:
                defer(period, _wait_condition, deferred, condition, period, timeout, start_time)

        def _handle_error(e):
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
            self.finished = True
            raise e

        def _stop_testing():
            with warnings.catch_warnings():
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

            stopTime = time.time()
            timeTaken = stopTime - startTime
            result.printErrors()
            if hasattr(result, 'separator2'):
                self.stream.writeln(result.separator2)
            run = result.testsRun
            self.stream.writeln("Ran %d test%s in %.3fs" %
                                (run, run != 1 and "s" or "", timeTaken))
            self.stream.writeln()

            expectedFails = unexpectedSuccesses = skipped = 0
            try:
                results = map(len, (result.expectedFailures,
                                    result.unexpectedSuccesses,
                                    result.skipped))
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

        sublime.set_timeout(_start_testing, 10)
