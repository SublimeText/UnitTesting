import time
import sublime
from unittest import TextTestRunner


class DeferringTextTestRunner(TextTestRunner):
    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        startTime = time.time()
        deferred = test(result)

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
                    if failed: self.stream.write(", ")
                    self.stream.write("errors=%d" % errored)
                self.stream.writeln(")")
            else:
                self.stream.writeln("OK")
            return result

        def _wait_condition():
            result = self.condition()

            if not result:
                assert (time.time() - self.condition_start_time) < 10, \
                    "Timeout, waited longer than 10s till condition true"
                sublime.set_timeout(_wait_condition, 10)

            else:
                sublime.set_timeout(_continue_testing, 10)

        def _continue_testing():
            try:
                delay = next(deferred)

                if callable(delay):
                    self.condition = delay
                    self.condition_start_time = time.time()
                    sublime.set_timeout(_wait_condition, 10)
                else:
                    if not isinstance(delay, int):
                        delay = 10

                    sublime.set_timeout(_continue_testing, delay)

            except StopIteration:
                _stop_testing()
                self.stream.close()

            except Exception as e:
                if not self.stream.closed:
                    self.stream.write("\nERROR: %s\n" % e)
                self.stream.close()

        sublime.set_timeout(_continue_testing, 10)
