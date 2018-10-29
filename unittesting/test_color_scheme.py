import sublime
from sublime_plugin import ApplicationCommand
from .mixin import UnitTestingMixin
from .const import DONE_MESSAGE


class UnitTestingColorSchemeCommand(ApplicationCommand, UnitTestingMixin):

    def run(self, package=None, **kwargs):
        if not package:
            return

        window = sublime.active_window()
        settings = self.load_unittesting_settings(package, kwargs)
        stream = self.load_stream(package, settings)

        try:
            from ColorSchemeUnit.lib.runner import ColorSchemeUnit
        except ImportError:
            stream.write('ERROR: ColorSchemeUnit runner could not be imported')
            stream.write('\n')
            stream.write(DONE_MESSAGE)
            stream.close()
            return

        tests = sublime.find_resources("color_scheme_test*")
        tests = [t for t in tests if t.startswith("Packages/%s/" % package)]

        if not tests:
            stream.write("ERROR: No syntax_test files are found in %s!" % package)
            stream.write("\n")
            stream.write(DONE_MESSAGE)
            stream.close()
            return

        # trigger "Start reading output"
        stream.write("Running ColorSchemeUnit\n")
        stream.flush()

        # a trick to use `async` as an argument
        kwargs = {
            "output": stream,
            "package": package,
            "async": False
        }
        result = ColorSchemeUnit(window).run(**kwargs)

        if result:
            stream.write('\n')
            stream.write("OK.\n")
        else:
            stream.write('\n')
            stream.write("FAILED.\n")

        stream.write("\n")
        stream.write(DONE_MESSAGE)
        stream.close()
