from .common.test import *
from .common.scheduler import *

import sublime
version = sublime.version()

if version >= '3000':
    from .core import DeferrableTestCase
