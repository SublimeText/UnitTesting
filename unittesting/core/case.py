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

import sys
import unittest
import warnings
from unittest.case import _ExpectedFailure, _UnexpectedSuccess, SkipTest


class DeferrableTestCase(unittest.TestCase):

    def run(self, result=None):

        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()

        self._resultForDoCleanups = result
        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        if (getattr(self.__class__, "__unittest_skip__", False) or
                getattr(testMethod, "__unittest_skip__", False)):
            # If the class or method was skipped.
            try:
                skip_why = getattr(self.__class__, '__unittest_skip_why__', '')
                skip_why = (
                    skip_why if skip_why != '' else
                    getattr(testMethod, '__unittest_skip_why__', '')
                )
                self._addSkip(result, skip_why)
            finally:
                result.stopTest(self)
            return

        try:
            success = False
            try:
                deferred = self.setUp()
                if deferred is not None:
                    for x in deferred:
                        yield x
            except SkipTest as e:
                self._addSkip(result, str(e))
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, sys.exc_info())
            else:
                try:
                    deferred = testMethod()
                    if deferred is not None:
                        for x in deferred:
                            yield x
                except KeyboardInterrupt:
                    raise
                except self.failureException:
                    result.addFailure(self, sys.exc_info())
                except _ExpectedFailure as e:
                    addExpectedFailure = getattr(
                        result, 'addExpectedFailure', None)
                    if addExpectedFailure is not None:
                        addExpectedFailure(self, e.exc_info)
                    else:
                        warnings.warn(
                            "TestResult has no addExpectedFailure method, "
                            "reporting as passes", RuntimeWarning
                        )
                        result.addSuccess(self)
                except _UnexpectedSuccess:
                    addUnexpectedSuccess = getattr(
                        result, 'addUnexpectedSuccess', None)
                    if addUnexpectedSuccess is not None:
                        addUnexpectedSuccess(self)
                    else:
                        warnings.warn(
                            "TestResult has no addUnexpectedSuccess method, "
                            "reporting as failures", RuntimeWarning
                        )
                        result.addFailure(self, sys.exc_info())
                except SkipTest as e:
                    self._addSkip(result, str(e))
                except:
                    result.addError(self, sys.exc_info())
                else:
                    success = True

                try:
                    deferred = self.tearDown()
                    if deferred is not None:
                        for x in deferred:
                            yield x
                except KeyboardInterrupt:
                    raise
                except:
                    result.addError(self, sys.exc_info())
                    success = False

            cleanUpSuccess = self.doCleanups()
            success = success and cleanUpSuccess
            if success:
                result.addSuccess(self)
        finally:
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
