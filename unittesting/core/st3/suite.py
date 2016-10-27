from unittest.suite import TestSuite, _isnotsuite


class DeferrableTestSuite(TestSuite):

    def run(self, result, debug=False):
        topLevel = False
        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = topLevel = True

        for test in self:
            if result.shouldStop:
                break

            if _isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                yield
                self._handleModuleFixture(test, result)
                yield
                self._handleClassSetUp(test, result)
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
            self._tearDownPreviousClass(None, result)
            yield
            self._handleModuleTearDown(result)
            yield
            result._testRunEntered = False
