# since ST2 uses python 2.6, which doesn't support unittest.TestLoader.discover
# in ST2, tests are imported as package module by unittest.TestLoader.loadTestsFromModule
# this file is only required if your package supports ST2

import imp
# make sure newest version of the module is loaded
from . import test_f
imp.reload(test_f)

# load testcases
from .test_f import *