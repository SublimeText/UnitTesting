import imp
from . import test_f
imp.reload(test_f)
from .test_f import *