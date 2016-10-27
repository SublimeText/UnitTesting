import sys
from unittest.case import TestCase, SkipTest, _UnexpectedSuccess, _ExpectedFailure


class DeferrableTestCase(TestCase):

    def _executeTestPart(self, function, outcome, isTest=False):
        try:
            deferred = function()
            if deferred is not None:
                for x in deferred:
                    yield x
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
            exc_info = sys.exc_info()
        except:
            outcome.success = False
            outcome.errors.append(sys.exc_info())
