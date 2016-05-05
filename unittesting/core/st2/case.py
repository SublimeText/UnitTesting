from unittest import TestCase


class DeferrableTestCase(TestCase):
    def run(self, result=None):
        if result is None: result = self.defaultTestResult()
        result.startTest(self)
        testMethod = getattr(self, self._testMethodName)
        try:
            try:
                deferred = self.setUp()
                if deferred is not None:
                    for x in deferred:
                        yield x
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                return

            ok = False
            try:
                deferred = testMethod()
                if deferred is not None:
                    for x in deferred:
                        yield x
                ok = True
            except self.failureException:
                result.addFailure(self, self._exc_info())
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())

            try:
                deferred = self.tearDown()
                if deferred is not None:
                    for x in deferred:
                        yield x
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                ok = False
            if ok: result.addSuccess(self)
        finally:
            result.stopTest(self)
