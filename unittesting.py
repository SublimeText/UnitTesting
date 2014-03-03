from unittest import TestLoader, TextTestRunner
import sublime, sublime_plugin
import threading
import imp
import os

# script directory
__dir__ = os.path.dirname(os.path.abspath(__file__))

class OutputPanelPrintCommand(sublime_plugin.TextCommand):
    def run(self, edit, characters):
        self.view.set_read_only(False)
        self.view.insert(edit, self.view.size(), characters)
        self.view.set_read_only(True)
        self.view.show(self.view.size())

class OutputPanel:
# from plugin-unittest-harness: https://bitbucket.org/klorenz/sublimepluginunittestharness
    r'''create an output panel and mimic an output stream for writing'''

    def __init__(self, name, file_regex='', line_regex = '', base_dir = None, word_wrap = False, line_numbers = False,
        gutter = False, scroll_past_end = False, syntax = 'Packages/Text/Plain text.tmLanguage'):

        self.name = name

        self.window = sublime.active_window()

        self.output_view = self.window.get_output_panel(name)

        # Default the to the current files directory if no working directory was given
        if (not base_dir and self.window.active_view() and self.window.active_view().file_name()):
            base_dir = os.path.dirname(self.window.active_view().file_name())

        self.output_view.settings().set("result_file_regex", file_regex)
        self.output_view.settings().set("result_line_regex", line_regex)
        self.output_view.settings().set("result_base_dir", base_dir)
        self.output_view.settings().set("word_wrap", word_wrap)
        self.output_view.settings().set("line_numbers", line_numbers)
        self.output_view.settings().set("gutter", gutter)
        self.output_view.settings().set("scroll_past_end", scroll_past_end)
        # self.output_view.assign_syntax(syntax)

    def write(self, s):
        args = {'characters': s}
        f = lambda: self.output_view.run_command('output_panel_print', args)
        sublime.set_timeout(f, 100)

    def flush(self):
        pass

    def show(self):
        self.window.run_command("show_panel", {"panel": "output."+self.name})

    def close(self):
        pass

class UnitTestingCommand(sublime_plugin.ApplicationCommand):
    def run(self, package=None, output=None):
        if package:
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

            # run unittest in second thread for gui synchronization, this may be tricky for st2
            module = imp.load_module("tests", *imp.find_module("tests", [os.path.join(sublime.packages_path(),package)]))

            loader = TestLoader()
            test = loader.loadTestsFromModule(module)
            # test = loader.loadTestsFromName("UnitTesting.tests")

            testRunner = TextTestRunner(stream, verbosity=2)
            testRunner.run(test)
            stream.close()
        else:
            sublime.active_window().show_input_panel('Package:', 'UnitTesting-example',
                lambda x: sublime.run_command("unit_testing", {"package":x, "output":output}), None, None )

