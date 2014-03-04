# since ST2 uses python 2.6, which doesn't support unittest.TestLoader.discover
# in ST2, tests are imported as package module by unittest.TestLoader.loadTestsFromModule
# this file is only required under 2 conditions,
# 1) if your package supports ST2;
# 2) if you want the tests could be reloaded in the run time of ST (eg, when you are editing the tests)

import imp
# make sure newest version of the module is loaded
from . import test
imp.reload(test)

# load testcases
from .test import *