# from https://bitbucket.org/klorenz/sublimepluginunittestharness

from unittest import runner

import sys, time, os, sublime

class DeferringTextTestRunner(runner.TextTestRunner):
    r'''deferred test runner.

    This test runner runs tests in deferred slices.  It gives
    back control to sublime text, such that it can draw views,
    do syntax highlighting and whatever.
    '''

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        runner.registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        startTime = time.time()
        startTestRun = getattr(result, 'startTestRun', None)

        if startTestRun is not None:
            startTestRun()

        deferred = test(result)

        def _stop_testing():
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
                failed, errored = map(len, (result.failures, result.errors))
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
            return result

        def _wait_condition():
            result = self.condition()

            if not result:
                assert (time.time() - self.condition_start_time) < 10, "Timeout, waited longer than 10s till condition true"
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
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

                _stop_testing()
                self.stream.close()

        sublime.set_timeout(_continue_testing, 10)
