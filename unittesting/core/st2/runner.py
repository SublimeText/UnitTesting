import time
import sublime
from unittest import TextTestRunner


class DeferringTextTestRunner(TextTestRunner):
    def run(self, test):
        "Run the given test case or test suite."
        self.finished = False
        result = self._makeResult()
        startTime = time.time()

        def _start_testing():
            deferred = test(result)
            sublime.set_timeout(lambda: _continue_testing(deferred), 10)

        def _continue_testing(deferred):
            try:
                condition = next(deferred)
                if callable(condition):
                    sublime.set_timeout(
                        lambda: _wait_condition(deferred, condition, time.time(), 10000), 10)
                elif isinstance(condition, tuple) and len(condition) == 2 and \
                        callable(condition[0]) and isinstance(condition[1], int):
                    sublime.set_timeout(
                        lambda: _wait_condition(deferred, condition[0], time.time(), condition[1]),
                        10)
                elif isinstance(condition, int):
                    sublime.set_timeout(lambda: _continue_testing(deferred), condition)
                else:
                    sublime.set_timeout(lambda: _continue_testing(deferred), 10)

            except StopIteration:
                _stop_testing()
                self.finished = True

            except Exception as e:
                self.finished = True
                raise e

        def _wait_condition(deferred, condition, start_time, wait_for):
            if not condition():
                if (time.time() - start_time) * 1000 < wait_for:
                    sublime.set_timeout(
                        lambda: _wait_condition(deferred, condition, start_time, wait_for), 10)
                    return
                else:
                    self.stream.writeln("Condition timeout, continue anyway.")

            sublime.set_timeout(lambda: _continue_testing(deferred), 10)

        def _stop_testing():
            stopTime = time.time()
            timeTaken = stopTime - startTime
            result.printErrors()
            self.stream.writeln(result.separator2)
            run = result.testsRun
            self.stream.writeln("Ran %d test%s in %.3fs" %
                                (run, run != 1 and "s" or "", timeTaken))
            self.stream.writeln()
            if not result.wasSuccessful():
                self.stream.write("FAILED (")
                failed, errored = map(len, (result.failures, result.errors))
                if failed:
                    self.stream.write("failures=%d" % failed)
                if errored:
                    if failed:
                        self.stream.write(", ")
                    self.stream.write("errors=%d" % errored)
                self.stream.writeln(")")
            else:
                self.stream.writeln("OK")
            return result

        sublime.set_timeout(_start_testing, 10)
