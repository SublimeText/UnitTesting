import sublime
version = sublime.version()

__all__ = ["TestLoader"]

if version >= '3000':
    from .loader import TestLoader
    from .runner import DeferringTextTestRunner
    from .case import DeferrableTestCase
    __all__ += ["DeferringTextTestRunner", "DeferrableTestCase"]
else:
    from loader import TestLoader
