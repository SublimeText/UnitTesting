import sublime
from sublime_plugin import ApplicationCommand
from .mixin import UnitTestingMixin
from .const import DONE_MESSAGE

try:
    from ColorSchemeUnit.lib.runner import ColorSchemeUnit
except Exception:
    print('ColorSchemeUnit runner could not be imported')


class UnitTestingColorSchemeCommand(ApplicationCommand, UnitTestingMixin):

    def run(self, package=None, **kargs):
        if not package:
            return

        window = sublime.active_window()
        settings = self.load_unittesting_settings(package, **kargs)
        stream = self.load_stream(package, settings["output"])

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

        result = ColorSchemeUnit(window).run(output=stream, package=package, async=False)

        if result:
            stream.write('\n')
            stream.write("OK.\n")
        else:
            stream.write('\n')
            stream.write("FAILED.\n")

        stream.write("\n")
        stream.write(DONE_MESSAGE)
        stream.close()
