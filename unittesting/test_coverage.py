import sublime
import os
import sys
import re
# from collections import namedtuple
from .test_package import UnitTestingCommand

version = sublime.version()
platform = sublime.platform()

if version >= "3000" and platform != "windows":
    import coverage


class UnitTestingCoverageCommand(UnitTestingCommand):

    def unit_testing(self, stream, package, settings):
        package_path = os.path.join(sublime.packages_path(), package)
        data_file = os.path.join(package_path, ".coverage")
        config_file = os.path.join(package_path, ".coveragerc")
        include = "{}/*".format(package_path)
        omit = "{}/{}/*".format(package_path, settings["tests_dir"])
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                txt = f.read()
                if re.search("^include", txt, re.M):
                    include = None
                if re.search("^omit", txt, re.M):
                    omit = None
        else:
            config_file = None

        def cleanup():
            stream.write("\n")
            cov.stop()
            old_wd = os.getcwd()
            os.chdir(package_path)
            coverage.files.set_relative_directory()
            cov.report(file=stream)
            if settings["output"] != "<panel>":
                cov.save()
            os.chdir(old_wd)

        cov = coverage.Coverage(
            data_file=data_file, config_file=config_file, include=include, omit=omit)
        cov.start()
        self.reload_package(package)
        UnitTestingCommand.unit_testing(self, stream, package, settings, [cleanup])

    def is_enabled(self):
        return version >= "3000" and platform != "windows" and "PackageReloader" in sys.modules
