import sublime
import sublime_plugin

import sys

from .mixin import UnitTestingMixin
from .const import DONE_MESSAGE


class UnitTestingColorSchemeCommand(sublime_plugin.ApplicationCommand, UnitTestingMixin):

    def run(self, package=None, **kwargs):
        if not package:
            return

        if sys.version_info >= (3, 8):
            # ColorSchemeUnit doesn't support python 3.8
            # hop back to python 3.3
            kwargs["package"] = package
            sublime.run_command("unit_testing33_color_scheme", kwargs)
            return

        window = sublime.active_window()
        settings = self.load_unittesting_settings(package, kwargs)
        stream = self.load_stream(package, settings)

        try:
            # if sublime.version() >= "4000":
            #     # this doesn't work now because ColorSchemeUnit is not python 3.8 compatible
            #     p = os.path.join(sublime.installed_packages_path(), "ColorSchemeUnit.sublime-package")
            #     if os.path.exists(p):
            #         sublime_plugin.multi_importer.loaders.append(sublime_plugin.ZipLoader(p))

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
