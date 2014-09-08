import sublime
version = sublime.version()
if version >= '3000':
    from .loader import TestLoader
    from .runner import DeferringTextTestRunner
    from .case import DeferrableTestCase
else:
    from loader import TestLoader
