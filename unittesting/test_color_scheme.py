import sublime
from sublime_plugin import ApplicationCommand
from .mixin import UnitTestingMixin

try:
    from ColorSchemeUnit.lib.runner import ColorSchemeUnit
except:
    print('ColorSchemeUnit runner could not be imported')


class UnitTestingColorSchemeCommand(ApplicationCommand, UnitTestingMixin):

    def run(self, package=None, **kargs):
        if not package:
            return

        window = sublime.active_window()
        settings = self.load_settings(package, **kargs)
        stream = self.load_stream(package, settings["output"])

        # Make sure at least one file from the
        # package opened for ColorSchemeUnit.
        tests = sublime.find_resources("color_scheme_test*")

        if package != "__all__":
            tests = [t for t in tests if t.startswith("Packages/%s/" % package)]

        if tests:
            window.open_file(sublime.packages_path().rstrip('Packages') + tests[0])

        ColorSchemeUnit(window).run(output=stream)
