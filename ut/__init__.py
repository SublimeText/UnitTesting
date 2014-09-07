try:
    from .loader import TestLoader
    from .runner import DeferringTextTestRunner
    from .case import DeferrableTestCase
except:
    from loader import TestLoader
