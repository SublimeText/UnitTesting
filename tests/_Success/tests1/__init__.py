import imp
from . import test_s
imp.reload(test_s)
from .test_s import *