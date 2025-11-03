import time
import sys

from collections.abc import Generator as DeferrableMethod
from unittest import TestCase
from unittest.case import _addSkip
from unittest.case import _Outcome
from unittest.case import expectedFailure

from .runner import defer

__all__ = ["DeferrableMethod", "DeferrableTestCase", "expectedFailure"]


class DeferrableTestCase(TestCase):

    def _callSetUp(self):
        deferred = self.setUp()
        if isinstance(deferred, DeferrableMethod):
            yield from deferred

    def _callTestMethod(self, method):
        deferred = method()
        if isinstance(deferred, DeferrableMethod):
            yield from deferred

    def _callTearDown(self):
        deferred = self.tearDown()
        if isinstance(deferred, DeferrableMethod):
            yield from deferred

    def _callCleanup(self, function, *args, **kwargs):
        deferred = function(*args, **kwargs)
        if isinstance(deferred, DeferrableMethod):
            yield from deferred

    @staticmethod
    def defer(delay, callback, *args, **kwargs):
        defer(delay, callback, *args, **kwargs)

    def run(self, result=None):
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            stopTestRun = getattr(result, 'stopTestRun', None)
            if startTestRun is not None:
                startTestRun()
        else:
            stopTestRun = None

        result.startTest(self)
        try:
            testMethod = getattr(self, self._testMethodName)
            if (getattr(self.__class__, "__unittest_skip__", False) or
                getattr(testMethod, "__unittest_skip__", False)):
                # If the class or method was skipped.
                skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                            or getattr(testMethod, '__unittest_skip_why__', ''))
                _addSkip(result, self, skip_why)
                return result

            expecting_failure = (
                getattr(self, "__unittest_expecting_failure__", False) or
                getattr(testMethod, "__unittest_expecting_failure__", False)
            )
            outcome = _Outcome(result)
            start_time = time.perf_counter()
            try:
                self._outcome = outcome

                with outcome.testPartExecutor(self):
                    deferred = self._callSetUp()
                    if isinstance(deferred, DeferrableMethod):
                        yield from deferred
                if outcome.success:
                    outcome.expecting_failure = expecting_failure
                    with outcome.testPartExecutor(self):
                        deferred = self._callTestMethod(testMethod)
                        if isinstance(deferred, DeferrableMethod):
                            yield from deferred
                    outcome.expecting_failure = False
                    with outcome.testPartExecutor(self):
                        deferred = self._callTearDown()
                        if isinstance(deferred, DeferrableMethod):
                            yield from deferred
                deferred = self.doCleanups()
                if isinstance(deferred, DeferrableMethod):
                    yield from deferred

                self._addDuration(result, (time.perf_counter() - start_time))

                if outcome.success:
                    if expecting_failure:
                        if outcome.expectedFailure:
                            self._addExpectedFailure(result, outcome.expectedFailure)
                        else:
                            self._addUnexpectedSuccess(result)
                    else:
                        result.addSuccess(self)
                return result
            finally:
                # explicitly break reference cycle:
                # outcome.expectedFailure -> frame -> outcome -> outcome.expectedFailure
                outcome.expectedFailure = None
                outcome = None

                # clear the outcome, no more needed
                self._outcome = None

        finally:
            result.stopTest(self)
            if stopTestRun is not None:
                stopTestRun()

    def doCleanups(self):
        """Execute all cleanup functions. Normally called for you after tearDown."""
        outcome = self._outcome or _Outcome()
        while self._cleanups:
            function, args, kwargs = self._cleanups.pop()
            with outcome.testPartExecutor(self):
                deferred = self._callCleanup(function, *args, **kwargs)
                if isinstance(deferred, DeferrableMethod):
                    yield from deferred

        # return this for backwards compatibility
        # even though we no longer use it internally
        return outcome.success

    @classmethod
    def doClassCleanups(cls):
        """Execute all class cleanup functions. Normally called for you after tearDownClass."""
        cls.tearDown_exceptions = []
        while cls._class_cleanups:
            function, args, kwargs = cls._class_cleanups.pop()
            try:
                deferred = function(*args, **kwargs)
                if isinstance(deferred, DeferrableMethod):
                    yield from deferred
            except Exception:
                cls.tearDown_exceptions.append(sys.exc_info())

    def __call__(self, *args, **kwds):
        deferred = self.run(*args, **kwds)
        if isinstance(deferred, DeferrableMethod):
            yield from deferred
        else:
            return deferred
