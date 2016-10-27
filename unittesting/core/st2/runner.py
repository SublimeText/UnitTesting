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
                        lambda: _wait_condition(deferred, condition, time.time()), 10)
                else:
                    if not isinstance(condition, int):
                        condition = 10

                    sublime.set_timeout(lambda: _continue_testing(deferred), condition)

            except StopIteration:
                _stop_testing()
                self.finished = True

            except Exception as e:
                self.finished = True
                raise e

        def _wait_condition(deferred, condition, start_time):
            if not condition():
                assert (time.time() - start_time) < 10, "Condition timeout."
                sublime.set_timeout(lambda: _wait_condition(deferred, condition, time.time()), 10)
            else:
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
