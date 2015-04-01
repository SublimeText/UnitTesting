import sublime
version = sublime.version()

__all__ = ["TestLoader", "DeferringTextTestRunner", "DeferrableTestCase", "DeferrableTestSuite"]

if version >= '3000':
    from .st3.runner import DeferringTextTestRunner
    from .st3.case import DeferrableTestCase
    from .st3.suite import DeferrableTestSuite
else:
    from .st2.runner import DeferringTextTestRunner
    from .st2.case import DeferrableTestCase
    from .st2.suite import DeferrableTestSuite

from .loader import TestLoader
