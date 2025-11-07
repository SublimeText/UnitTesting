import sys

if sys.version_info[:2] >= (3, 13):
    from .py313.case import DeferrableMethod
    from .py313.case import DeferrableTestCase
    from .py313.case import IsolatedAsyncioTestCase
    from .py313.case import TestCase
    from .py313.case import expectedFailure
    from .py313.loader import DeferrableTestLoader
    from .py313.runner import AWAIT_WORKER
    from .py313.runner import DeferringTextTestRunner
    from .py313.suite import DeferrableTestSuite
elif sys.version_info[:2] == (3, 8):
    from .py38.case import DeferrableMethod
    from .py38.case import DeferrableTestCase
    from .py38.case import IsolatedAsyncioTestCase
    from .py38.case import TestCase
    from .py38.case import expectedFailure
    from .py38.loader import DeferrableTestLoader
    from .py38.runner import AWAIT_WORKER
    from .py38.runner import DeferringTextTestRunner
    from .py38.suite import DeferrableTestSuite
elif sys.version_info[:2] == (3, 3):
    from .py33.case import DeferrableMethod
    from .py33.case import DeferrableTestCase
    from .py33.case import IsolatedAsyncioTestCase
    from .py33.case import TestCase
    from .py33.case import expectedFailure
    from .py33.loader import DeferrableTestLoader
    from .py33.runner import AWAIT_WORKER
    from .py33.runner import DeferringTextTestRunner
    from .py33.suite import DeferrableTestSuite
else:
    raise ImportError("Unsupported python runtime!")

__all__ = [
    "AWAIT_WORKER",
    "DeferrableMethod",
    "DeferrableTestCase",
    "DeferrableTestLoader",
    "DeferrableTestSuite",
    "DeferringTextTestRunner",
    "IsolatedAsyncioTestCase",
    "TestCase",
    "expectedFailure",
]
