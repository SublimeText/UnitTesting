from unittest.suite import TestSuite, _isnotsuite, _call_if_exists, _DebugResult
from unittest import util
from ...utils import isiterable


class DeferrableTestSuite(TestSuite):

    def run(self, result, debug=False):
        topLevel = False
        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = topLevel = True

        for index, test in enumerate(self):
            if result.shouldStop:
                break

            if _isnotsuite(test):
                deferred = self._tearDownPreviousClass(test, result)
                if isiterable(deferred):
                    yield from deferred
                yield
                self._handleModuleFixture(test, result)
                yield
                deferred = self._handleClassSetUp(test, result)
                if isiterable(deferred):
                    yield from deferred
                yield
                result._previousTestClass = test.__class__

                if getattr(test.__class__, '_classSetupFailed', False) or \
                        getattr(result, '_moduleSetUpFailed', False):
                    continue

            if not debug:
                deferred = test(result)
            else:
                deferred = test.debug()

            if self._cleanup:
                self._removeTestAtIndex(index)

            if isiterable(deferred):
                yield from deferred

            yield

        if topLevel:
            deferred = self._tearDownPreviousClass(None, result)
            if isiterable(deferred):
                yield from deferred
            yield
            yield
            self._handleModuleTearDown(result)
            yield
            result._testRunEntered = False

    def _handleClassSetUp(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        if currentClass == previousClass:
            return
        if result._moduleSetUpFailed:
            return
        if getattr(currentClass, "__unittest_skip__", False):
            return

        try:
            currentClass._classSetupFailed = False
        except TypeError:
            # test may actually be a function
            # so its class will be a builtin-type
            pass

        setUpClass = getattr(currentClass, 'setUpClass', None)
        if setUpClass is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                deferred = setUpClass()
                if isiterable(deferred):
                    yield from deferred
            except Exception as e:
                if isinstance(result, _DebugResult):
                    raise
                currentClass._classSetupFailed = True
                className = util.strclass(currentClass)
                self._createClassOrModuleLevelException(result, e,
                                                        'setUpClass',
                                                        className)
            finally:
                _call_if_exists(result, '_restoreStdout')
                if currentClass._classSetupFailed is True:
                    deferred = currentClass.doClassCleanups()
                    if isiterable(deferred):
                        yield from deferred
                    if len(currentClass.tearDown_exceptions) > 0:
                        for exc in currentClass.tearDown_exceptions:
                            self._createClassOrModuleLevelException(
                                result, exc[1], 'setUpClass', className,
                                info=exc)

    def _tearDownPreviousClass(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        if currentClass == previousClass:
            return
        if getattr(previousClass, '_classSetupFailed', False):
            return
        if getattr(result, '_moduleSetUpFailed', False):
            return
        if getattr(previousClass, "__unittest_skip__", False):
            return

        tearDownClass = getattr(previousClass, 'tearDownClass', None)
        if tearDownClass is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                deferred = tearDownClass()
                if isiterable(deferred):
                    yield from deferred
            except Exception as e:
                if isinstance(result, _DebugResult):
                    raise
                className = util.strclass(previousClass)
                self._createClassOrModuleLevelException(result, e,
                                                        'tearDownClass',
                                                        className)
            finally:
                _call_if_exists(result, '_restoreStdout')
                deferred = previousClass.doClassCleanups()
                if isiterable(deferred):
                    yield from deferred
                if len(previousClass.tearDown_exceptions) > 0:
                    for exc in previousClass.tearDown_exceptions:
                        className = util.strclass(previousClass)
                        self._createClassOrModuleLevelException(result, exc[1],
                                                                'tearDownClass',
                                                                className,
                                                                info=exc)
