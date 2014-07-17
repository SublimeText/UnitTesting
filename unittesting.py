from unittest import  TextTestRunner
try:
    from .loader import TestLoader
except:
    from loader import TestLoader

import sublime, sublime_plugin
import threading
import imp
import os
import re

# script directory
__dir__ = os.path.dirname(os.path.abspath(__file__))

class OutputPanelInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, characters):
        self.view.set_read_only(False)
        self.view.insert(edit, self.view.size(), characters)
        self.view.set_read_only(True)
        self.view.show(self.view.size())

class OutputPanel:
    def __init__(self, name, file_regex='', line_regex = '', base_dir = None, word_wrap = False, line_numbers = False,
        gutter = False, scroll_past_end = False, syntax = 'Packages/Text/Plain text.tmLanguage'):

        self.name = name
        self.window = sublime.active_window()
        self.output_view = self.window.get_output_panel(name)

        # default to the current file directory
        if (not base_dir and self.window.active_view() and self.window.active_view().file_name()):
            base_dir = os.path.dirname(self.window.active_view().file_name())

        self.output_view.settings().set("result_file_regex", file_regex)
        self.output_view.settings().set("result_line_regex", line_regex)
        self.output_view.settings().set("result_base_dir", base_dir)
        self.output_view.settings().set("word_wrap", word_wrap)
        self.output_view.settings().set("line_numbers", line_numbers)
        self.output_view.settings().set("gutter", gutter)
        self.output_view.settings().set("scroll_past_end", scroll_past_end)
        self.output_view.settings().set("syntax", syntax)

    def write(self, s):
        self.output_view.run_command('output_panel_insert', {'characters': s})

    def flush(self):
        pass

    def show(self):
        self.window.run_command("show_panel", {"panel": "output."+self.name})

    def close(self):
        pass

class UnitTestingCommand(sublime_plugin.ApplicationCommand):
    def run(self, package=None, output=None):
        settingsFileName = "Preferences.sublime-settings"
        settingsName = "currentUnitTestingPackage"
        settings = sublime.load_settings(settingsFileName)
        if package:
            tests_dir = 'tests'

            if output=="panel":
                output_panel = OutputPanel('unittests', file_regex = r'File "([^"]*)", line (\d+)')
                output_panel.show()
                stream = output_panel
            else:
                if output:
                    outfile = output
                else:
                    outputdir = os.path.join(sublime.packages_path(), 'User', 'UnitTesting', "tests_output")
                    if not os.path.isdir(outputdir):
                        os.makedirs(outputdir)
                    outfile = os.path.join(outputdir, package)

                if os.path.exists(outfile): os.remove(outfile)
                stream = open(outfile, "w")

            try:
                # use custom loader which support ST2 and reloading modules
                loader = TestLoader()
                test = loader.discover(os.path.join(sublime.packages_path(),package, tests_dir))
                testRunner = TextTestRunner(stream, verbosity=2)
                testRunner.run(test)
            except Exception as e:
                stream.write("ERROR: %s\n" % e)

            stream.close()
            # save the package name
            settings.set(settingsName, package)
            sublime.save_settings(settingsFileName)
        else:
            currentUnitTestingPackage = settings.get(settingsName, "Package Name")
            view = sublime.active_window().show_input_panel('Package:', currentUnitTestingPackage,
                lambda x: sublime.run_command("unit_testing", {"package":x, "output":output}), None, None )
            view.run_command("select_all")
