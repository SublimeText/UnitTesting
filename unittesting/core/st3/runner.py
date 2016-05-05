# This file is based on the previous work from Kay-Uwe Lorenz in the plugin
# sublimepluginunittestharness with the following License
#
# Copyright (c) 2013, Kay-Uwe (Kiwi) Lorenz <kiwi@franka.dyndns.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import time
from unittest import runner

import sublime


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
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

                _stop_testing()
                self.stream.close()

        sublime.set_timeout(_continue_testing, 10)
