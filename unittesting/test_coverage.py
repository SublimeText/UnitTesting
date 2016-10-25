import sublime
import os
import sys
import re
from .test_package import UnitTestingCommand

version = sublime.version()
platform = sublime.platform()

try:
    if version >= "3000":
        import coverage
except:
    print("coverage not found.")


class UnitTestingCoverageCommand(UnitTestingCommand):

    def unit_testing(self, stream, package, settings):
        package_path = os.path.join(sublime.packages_path(), package)
        data_file = os.path.join(
            sublime.packages_path(), "User", "UnitTesting", package, "coverage")
        data_file_dir = os.path.dirname(data_file)
        if not os.path.isdir(data_file_dir):
            os.makedirs(data_file_dir)
        if os.path.exists(data_file):
            os.unlink(data_file)
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

        cov = coverage.Coverage(
            data_file=data_file, config_file=config_file, include=include, omit=omit)
        cov.start()
        self.reload_package(package)

        def cleanup():
            stream.write("\n")
            cov.stop()
            coverage.files.RELATIVE_DIR = os.path.normcase(package_path + os.sep)
            ignore_errors = cov.get_option("report:ignore_errors")
            show_missing = cov.get_option("report:show_missing")
            cov.report(file=stream, ignore_errors=ignore_errors, show_missing=show_missing)
            cov.save()

        super().unit_testing(stream, package, settings, [cleanup])

    def is_enabled(self):
        return "PackageReloader" in sys.modules and "coverage" in sys.modules
