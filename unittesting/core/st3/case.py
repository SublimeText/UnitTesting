from functools import wraps
import sys
import unittest
import warnings
from unittest.case import _ExpectedFailure, _UnexpectedSuccess, SkipTest, _Outcome
from ...utils import isiterable


def expectedFailure(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            deferred = func(*args, **kwargs)
            if isiterable(deferred):
                yield from deferred
        except Exception:
            raise _ExpectedFailure(sys.exc_info())
        raise _UnexpectedSuccess
    return wrapper


class DeferrableTestCase(unittest.TestCase):

    def _executeTestPart(self, function, outcome, isTest=False):
        try:
            deferred = function()
            if isiterable(deferred):
                yield from deferred
        except KeyboardInterrupt:
            raise
        except SkipTest as e:
            outcome.success = False
            outcome.skipped = str(e)
        except _UnexpectedSuccess:
            exc_info = sys.exc_info()
            outcome.success = False
            if isTest:
                outcome.unexpectedSuccess = exc_info
            else:
                outcome.errors.append(exc_info)
        except _ExpectedFailure:
            outcome.success = False
            exc_info = sys.exc_info()
            if isTest:
                outcome.expectedFailure = exc_info
            else:
                outcome.errors.append(exc_info)
        except self.failureException:
            outcome.success = False
            outcome.failures.append(sys.exc_info())
        except Exception:
            outcome.success = False
            outcome.errors.append(sys.exc_info())

    def run(self, result=None):
        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()

        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        if getattr(self.__class__, "__unittest_skip__", False) or \
                getattr(testMethod, "__unittest_skip__", False):
            # If the class or method was skipped.
            try:
                skip_why = getattr(self.__class__, '__unittest_skip_why__', '') or \
                    getattr(testMethod, '__unittest_skip_why__', '')
                self._addSkip(result, skip_why)
            finally:
                result.stopTest(self)
            return
        try:
            outcome = _Outcome()
            self._outcomeForDoCleanups = outcome

            yield from self._executeTestPart(self.setUp, outcome)
            if outcome.success:
                yield from self._executeTestPart(testMethod, outcome, isTest=True)
                yield from self._executeTestPart(self.tearDown, outcome)

            yield from self.doCleanups()
            if outcome.success:
                result.addSuccess(self)
            else:
                if outcome.skipped is not None:
                    self._addSkip(result, outcome.skipped)
                for exc_info in outcome.errors:
                    result.addError(self, exc_info)
                for exc_info in outcome.failures:
                    result.addFailure(self, exc_info)
                if outcome.unexpectedSuccess is not None:
                    addUnexpectedSuccess = getattr(result, 'addUnexpectedSuccess', None)
                    if addUnexpectedSuccess is not None:
                        addUnexpectedSuccess(self)
                    else:
                        warnings.warn(
                            "TestResult has no addUnexpectedSuccess method, reporting as failures",
                            RuntimeWarning)
                        result.addFailure(self, outcome.unexpectedSuccess)

                if outcome.expectedFailure is not None:
                    addExpectedFailure = getattr(result, 'addExpectedFailure', None)
                    if addExpectedFailure is not None:
                        addExpectedFailure(self, outcome.expectedFailure)
                    else:
                        warnings.warn(
                            "TestResult has no addExpectedFailure method, reporting as passes",
                            RuntimeWarning)
                        result.addSuccess(self)
            return result
        finally:
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

    def doCleanups(self):
        """Execute all cleanup functions.

        Normally called for you after tearDown.
        """
        outcome = self._outcomeForDoCleanups or _Outcome()
        while self._cleanups:
            function, args, kwargs = self._cleanups.pop()
            part = lambda: function(*args, **kwargs)  # noqa: E731
            yield from self._executeTestPart(part, outcome)

        # return this for backwards compatibility
        # even though we no longer us it internally
        return outcome.success
