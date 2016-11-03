from unittest.suite import TestSuite, _isnotsuite, _call_if_exists, _DebugResult
from unittest import util


class DeferrableTestSuite(TestSuite):

    def run(self, result, debug=False):
        topLevel = False
        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = topLevel = True

        for test in self:
            if result.shouldStop:
                break

            if _isnotsuite(test):
                deferred = self._tearDownPreviousClass(test, result)
                if deferred is not None and hasattr(deferred, '__iter__'):
                    for x in deferred:
                        yield x
                yield
                self._handleModuleFixture(test, result)
                yield
                deferred = self._handleClassSetUp(test, result)
                if deferred is not None and hasattr(deferred, '__iter__'):
                    for x in deferred:
                        yield x
                yield
                result._previousTestClass = test.__class__

                if (getattr(test.__class__, '_classSetupFailed', False) or
                        getattr(result, '_moduleSetUpFailed', False)):
                    continue

            if not debug:
                deferred = test(result)
                if deferred is not None and hasattr(deferred, '__iter__'):
                    for x in deferred:
                        yield x
            else:
                deferred = test.debug()
                if deferred is not None and hasattr(deferred, '__iter__'):
                    for x in deferred:
                        yield x
            yield

        if topLevel:
            deferred = self._tearDownPreviousClass(None, result)
            if deferred is not None and hasattr(deferred, '__iter__'):
                for x in deferred:
                    yield x
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
                if deferred is not None and hasattr(deferred, '__iter__'):
                    for x in deferred:
                        yield x
            except Exception as e:
                if isinstance(result, _DebugResult):
                    raise
                currentClass._classSetupFailed = True
                className = util.strclass(currentClass)
                errorName = 'setUpClass (%s)' % className
                self._addClassOrModuleLevelException(result, e, errorName)
            finally:
                _call_if_exists(result, '_restoreStdout')

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
                if deferred is not None and hasattr(deferred, '__iter__'):
                    for x in deferred:
                        yield x
            except Exception as e:
                if isinstance(result, _DebugResult):
                    raise
                className = util.strclass(previousClass)
                errorName = 'tearDownClass (%s)' % className
                self._addClassOrModuleLevelException(result, e, errorName)
            finally:
                _call_if_exists(result, '_restoreStdout')
