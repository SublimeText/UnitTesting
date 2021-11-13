import sublime
import os
import sys
import re
from .package import UnitTestingCommand


try:
    import coverage  # noqa
    coverage.Coverage  # noqa
    coverage_loaded = True
except Exception:
    coverage_loaded = False


class UnitTestingCoverageCommand(UnitTestingCommand):
    fallback33 = "unit_testing33_coverage"

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

        if coverage_loaded:
            cov = coverage.Coverage(
                data_file=data_file, config_file=config_file, include=include, omit=omit)

            if not settings['start_coverage_after_reload']:
                cov.start()
            if settings["reload_package_on_testing"]:
                self.reload_package(package, dummy=False, show_reload_progress=False)
            if settings['start_coverage_after_reload']:
                cov.start()

            if settings['coverage_on_worker_thread']:
                import threading
                original_set_timeout_async = sublime.set_timeout_async

                def set_timeout_async(callback, *args, **kwargs):

                    def _():
                        sys.settrace(threading._trace_hook)
                        callback()

                    original_set_timeout_async(_, *args, **kwargs)

                sublime.set_timeout_async = set_timeout_async

            def cleanup():
                if settings['coverage_on_worker_thread']:
                    sublime.set_timeout_async = original_set_timeout_async

                stream.write("\n")
                cov.stop()
                coverage.files.RELATIVE_DIR = os.path.normcase(package_path + os.sep)
                ignore_errors = cov.get_option("report:ignore_errors")
                show_missing = cov.get_option("report:show_missing")
                cov.report(file=stream, ignore_errors=ignore_errors, show_missing=show_missing)
                if settings['generate_html_report']:
                    html_output_dir = os.path.join(package_path, 'htmlcov')
                    cov.html_report(directory=html_output_dir, ignore_errors=ignore_errors)
                cov.save()
            super().unit_testing(stream, package, settings, [cleanup])
        else:
            stream.write("Warning: coverage cannot be loaded.\n\n")
            super().unit_testing(stream, package, settings, [])
