import sublime
import sublime_plugin
from .mixin import UnitTestingMixin
from .const import DONE_MESSAGE

import sublime_api


class UnitTestingSyntaxBase(sublime_plugin.ApplicationCommand, UnitTestingMixin):

    def run(self, package=None, **kwargs):
        if not package:
            package = self.current_package_name
            if not package:
                return

        settings = self.load_unittesting_settings(package, kwargs)
        stream = self.load_stream(package, settings)
        self.syntax_testing(stream, package)


class UnitTestingSyntaxCommand(UnitTestingSyntaxBase):

    def syntax_testing(self, stream, package):
        total_assertions = 0
        failed_assertions = 0

        try:
            tests = sublime.find_resources("syntax_test*")
            tests = [t for t in tests if t.startswith("Packages/%s/" % package)]

            if not tests:
                raise RuntimeError("No syntax_test files are found in %s!" % package)
            for t in tests:
                assertions, test_output_lines = sublime_api.run_syntax_test(t)
                total_assertions += assertions
                if len(test_output_lines) > 0:
                    failed_assertions += len(test_output_lines)
                    for line in test_output_lines:
                        stream.write(line + "\n")

            file_noun = "files" if len(tests) > 1 else "file"
            if failed_assertions > 0:
                stream.write("FAILED: %d of %d assertions in %d %s failed\n" %
                             (failed_assertions, total_assertions, len(tests), file_noun))
            else:
                stream.write("Success: %d assertions in %s %s passed\n" %
                             (total_assertions, len(tests), file_noun))
                stream.write("OK\n")
        except Exception as e:
            if not stream.closed:
                stream.write("ERROR: %s\n" % e)

        stream.write("\n")
        stream.write(DONE_MESSAGE)
        stream.close()


class UnitTestingSyntaxCompatibilityCommand(UnitTestingSyntaxBase):

    def syntax_testing(self, stream, package):
        try:
            syntaxes = sublime.find_resources("*.sublime-syntax")
            syntaxes = [s for s in syntaxes if s.startswith("Packages/%s/" % package)]

            if not syntaxes:
                raise RuntimeError("No sublime-syntax files found in %s!" % package)

            total_errors = 0
            total_failed_syntaxes = 0

            for syntax in syntaxes:
                results = sublime_api.incompatible_syntax_patterns(syntax)
                for location, _, message in results:
                    stream.write("%s:%d:%d: %s\n" % (syntax, location[0] + 1,
                                                     location[0] + location[1],
                                                     message))
                if results:
                    total_errors += len(results)
                    total_failed_syntaxes += 1

            error_noun = "errors" if total_errors > 1 else "error"
            syntax_noun = "syntaxes" if len(syntaxes) > 1 else "syntax"
            if total_errors:
                stream.write("FAILED: %d %s in %d of %d %s\n" % (
                    total_errors, error_noun, total_failed_syntaxes, len(syntaxes), syntax_noun))
            else:
                stream.write("Success: %d %s passed\n" % (len(syntaxes), syntax_noun))
                stream.write("OK\n")
        except Exception as e:
            if not stream.closed:
                stream.write("ERROR: %s\n" % e)

        stream.write("\n")
        stream.write(DONE_MESSAGE)
        stream.close()
