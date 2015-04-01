import sublime
version = sublime.version()

__all__ = ["TestLoader"]

from .loader import TestLoader

if version >= '3000':
    from .runner import DeferringTextTestRunner
    from .case import DeferrableTestCase
    __all__ += ["DeferringTextTestRunner", "DeferrableTestCase"]
