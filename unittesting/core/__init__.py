import sys

if sys.version_info >= (3, 8):
    from .py38.case import DeferrableMethod
    from .py38.case import DeferrableTestCase
    from .py38.case import expectedFailure
    from .py38.runner import AWAIT_WORKER
    from .py38.runner import DeferringTextTestRunner
    from .py38.suite import DeferrableTestSuite
else:
    from .py33.case import DeferrableMethod
    from .py33.case import DeferrableTestCase
    from .py33.case import expectedFailure
    from .py33.runner import AWAIT_WORKER
    from .py33.runner import DeferringTextTestRunner
    from .py33.suite import DeferrableTestSuite

from .loader import UnitTestingLoader as TestLoader

__all__ = [
    "AWAIT_WORKER",
    "DeferrableMethod",
    "DeferrableTestCase",
    "DeferrableTestSuite",
    "DeferringTextTestRunner",
    "expectedFailure",
    "TestLoader",
]
