import sublime
import sublime_plugin
from .mixin import UnitTestingMixin
from .const import DONE_MESSAGE

version = sublime.version()

if version >= "3103":
    import sublime_api


class UnitTestingSyntaxCommand(sublime_plugin.ApplicationCommand, UnitTestingMixin):

    def run(self, package=None, **kargs):

        if not package:
            return
        settings = self.load_unittesting_settings(package, **kargs)
        stream = self.load_stream(package, settings)

        self.syntax_testing(stream, package)

    def syntax_testing(self, stream, package):
        total_assertions = 0
        failed_assertions = 0

        if version < "3103":
            stream.write("Warning: Syntax test is only avaliable on Sublime Text >=3103.\n")
            stream.write("\n")
            stream.write("OK\n")
            stream.write("\n")
            stream.write(DONE_MESSAGE)
            stream.close()
            return

        try:
            tests = sublime.find_resources("syntax_test*")
            if package != "__all__":
                tests = [t for t in tests if t.startswith("Packages/%s/" % package)]

            # remove UnitTesting syntax_tests
            tests = [t for t in tests if not t.startswith("Packages/UnitTesting/")]

            if not tests:
                raise RuntimeError("No syntax_test files are found in %s!" % package)
            for t in tests:
                assertions, test_output_lines = sublime_api.run_syntax_test(t)
                total_assertions += assertions
                if len(test_output_lines) > 0:
                    failed_assertions += len(test_output_lines)
                    for line in test_output_lines:
                        stream.write(line + "\n")
            if failed_assertions > 0:
                stream.write("FAILED: %d of %d assertions in %d files failed\n" %
                             (failed_assertions, total_assertions, len(tests)))
            else:
                stream.write("Success: %d assertions in %s files passed\n" %
                             (total_assertions, len(tests)))
                stream.write("OK\n")
        except Exception as e:
            if not stream.closed:
                stream.write("ERROR: %s\n" % e)

        stream.write("\n")
        stream.write(DONE_MESSAGE)
        stream.close()
