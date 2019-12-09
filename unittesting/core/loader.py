from unittest import TestSuite
from unittest import TestLoader
from . import DeferrableTestSuite


class UnitTestingLoader(TestLoader):
    def __init__(self, deferred=False):
        if deferred:
            self.suiteClass = DeferrableTestSuite
        else:
            self.suiteClass = TestSuite
        super().__init__()
