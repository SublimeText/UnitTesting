from unittest import TestSuite


class DeferrableTestSuite(TestSuite):

    def run(self, result):
        for test in self._tests:
            if result.shouldStop:
                break
            deferred = test(result)
            if deferred is not None and hasattr(deferred, '__iter__'):
                for x in deferred:
                    yield x
        yield
