import sys
from importlib.machinery import PathFinder


loader = PathFinder.find_module("UnitTesting")
mod = loader.load_module("UnitTesting")
sys.modules["UnitTesting"] = mod

from UnitTesting import ut as ut38  # noqa


class UnitTesting33Command(ut38.UnitTestingCommand):
    pass


class UnitTesting33CoverageCommand(ut38.UnitTestingCoverageCommand):
    pass


class UnitTesting33CurrentPackageCommand(ut38.UnitTestingCurrentPackageCommand):
    pass


class UnitTesting33CurrentPackageCoverageCommand(ut38.UnitTestingCurrentPackageCoverageCommand):
    pass


class UnitTesting33CurrentFileCommand(ut38.UnitTestingCurrentFileCommand):
    pass


class UnitTesting33ColorSchemeCommand(ut38.UnitTestingColorSchemeCommand):
    pass
