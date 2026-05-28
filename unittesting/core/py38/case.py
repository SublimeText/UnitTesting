import inspect
import time
import sys

import sublime_aio

from collections.abc import Generator as DeferrableMethod
from unittest import TestCase
from unittest.case import _Outcome
from unittest.case import expectedFailure

from .runner import defer

__all__ = [
    "AsyncTestCase",
    "DeferrableMethod",
    "DeferrableTestCase",
    "TestCase",
    "expectedFailure",
]


class DeferrableTestCase(TestCase):

    def _callSetUp(self):
        return self._callMaybeCoro(self.setUp)

    def _callTestMethod(self, method):
        return self._callMaybeCoro(method)

    def _callTearDown(self):
        return self._callMaybeCoro(self.tearDown)

    def _callCleanup(self, function, *args, **kwargs):
        return self._callMaybeCoro(function, *args, **kwargs)

    def _callMaybeCoro(self, func, /, *args, **kwargs):
        coro = func(*args, **kwargs)
        if isinstance(coro, DeferrableMethod):
            yield from coro
        elif inspect.iscoroutine(coro):
            raise TypeError(
                f"Async coroutine function {self.__class__.__name__}.{func.__name__}() "
                "is not supported by DeferrableTestCase! Use AsyncTestCase instead!"
            )

    @staticmethod
    def defer(delay, callback, *args, **kwargs):
        defer(delay, callback, *args, **kwargs)

    def run(self, result=None):
        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, "startTestRun", None)
            if startTestRun is not None:
                startTestRun()

        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        if getattr(self.__class__, "__unittest_skip__", False) or getattr(
            testMethod, "__unittest_skip__", False
        ):
            # If the class or method was skipped.
            try:
                skip_why = getattr(
                    self.__class__, "__unittest_skip_why__", ""
                ) or getattr(testMethod, "__unittest_skip_why__", "")
                self._addSkip(result, self, skip_why)
            finally:
                result.stopTest(self)
            return
        expecting_failure_method = getattr(
            testMethod, "__unittest_expecting_failure__", False
        )
        expecting_failure_class = getattr(self, "__unittest_expecting_failure__", False)
        expecting_failure = expecting_failure_class or expecting_failure_method
        outcome = _Outcome(result)
        try:
            self._outcome = outcome

            with outcome.testPartExecutor(self):
                yield from self._callSetUp()
            if outcome.success:
                outcome.expecting_failure = expecting_failure
                with outcome.testPartExecutor(self, isTest=True):
                    yield from self._callTestMethod(testMethod)
                outcome.expecting_failure = False
                with outcome.testPartExecutor(self):
                    yield from self._callTearDown()
            yield from self.doCleanups()

            for test, reason in outcome.skipped:
                self._addSkip(result, test, reason)
            self._feedErrorsToResult(result, outcome.errors)

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
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, "stopTestRun", None)
                if stopTestRun is not None:
                    stopTestRun()

            # explicitly break reference cycles:
            # outcome.errors -> frame -> outcome -> outcome.errors
            # outcome.expectedFailure -> frame -> outcome -> outcome.expectedFailure
            outcome.errors.clear()
            outcome.expectedFailure = None

            # clear the outcome, no more needed
            self._outcome = None

    def doCleanups(self):
        """Execute all cleanup functions. Normally called for you after tearDown."""
        outcome = self._outcome or _Outcome()
        while self._cleanups:
            function, args, kwargs = self._cleanups.pop()
            with outcome.testPartExecutor(self):
                yield from self._callCleanup(function, *args, **kwargs)

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
                yield from cls._callMaybeCoro(function, *args, **kwargs)
            except Exception:
                cls.tearDown_exceptions.append(sys.exc_info())

    def __call__(self, *args, **kwds):
        yield from self.run(*args, **kwds)


class AsyncTestCase(DeferrableTestCase):

    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    def _callMaybeCoro(self, func, /, *args, **kwargs):
        coro = func(*args, **kwargs)
        if isinstance(coro, DeferrableMethod):
            yield from coro
        elif inspect.iscoroutine(coro):
            fut = sublime_aio.run_coroutine(coro)

            def wait_until_complete():
                if not fut.done() and not fut.cancelled():
                    return False
                exception = fut.exception()
                if exception is not None:
                    raise exception from None
                return True

            yield wait_until_complete
