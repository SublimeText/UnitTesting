import sys

if sys.version_info >= (3, 8):
    from .py38.case import DeferrableMethod
    from .py38.case import DeferrableTestCase
    from .py38.case import expectedFailure
    from .py38.loader import DeferrableTestLoader
    from .py38.runner import AWAIT_WORKER
    from .py38.runner import DeferringTextTestRunner
    from .py38.suite import DeferrableTestSuite
else:
    from .py33.case import DeferrableMethod
    from .py33.case import DeferrableTestCase
    from .py33.case import expectedFailure
    from .py33.loader import DeferrableTestLoader
    from .py33.runner import AWAIT_WORKER
    from .py33.runner import DeferringTextTestRunner
    from .py33.suite import DeferrableTestSuite

__all__ = [
    "AWAIT_WORKER",
    "DeferrableMethod",
    "DeferrableTestCase",
    "DeferrableTestLoader",
    "DeferrableTestSuite",
    "DeferringTextTestRunner",
    "expectedFailure",
]
