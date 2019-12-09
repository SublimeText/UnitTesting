import sys

if sys.version_info >= (3, 8):
    from .py38.runner import DeferringTextTestRunner, AWAIT_WORKER
    from .py38.case import DeferrableTestCase
    from .py38.suite import DeferrableTestSuite
    from unittest import expectedFailure
else:
    from .py33.runner import DeferringTextTestRunner, AWAIT_WORKER
    from .py33.case import DeferrableTestCase, expectedFailure
    from .py33.suite import DeferrableTestSuite

from .loader import UnitTestingLoader as TestLoader  # noqa

__all__ = [
    "TestLoader",
    "DeferringTextTestRunner",
    "DeferrableTestCase",
    "DeferrableTestSuite",
    "AWAIT_WORKER",
    "expectedFailure"
]
