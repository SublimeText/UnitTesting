import sublime
import os


class OutputPanel:

    def __init__(
        self, name, file_regex='', line_regex='', base_dir=None,
        word_wrap=False, line_numbers=False, gutter=False,
        scroll_past_end=False
    ):
        self.name = name
        self.window = sublime.active_window()
        self.output_view = self.window.get_output_panel(name)

        # default to the current file directory
        if (not base_dir and self.window.active_view() and
                self.window.active_view().file_name()):
            base_dir = os.path.dirname(self.window.active_view().file_name())

        settings = self.output_view.settings()
        settings.set("result_file_regex", file_regex)
        settings.set("result_line_regex", line_regex)
        settings.set("result_base_dir", base_dir)
        settings.set("word_wrap", word_wrap)
        settings.set("line_numbers", line_numbers)
        settings.set("gutter", gutter)
        settings.set("scroll_past_end", scroll_past_end)

        self.output_view.assign_syntax("Packages/UnitTesting/res/unit-testing-test-result.sublime-syntax")
        self.closed = False

    def write(self, s):
        self.output_view.set_read_only(False)
        self.output_view.run_command('append', {'characters': s}),
        self.output_view.set_read_only(True)
        self.output_view.show(self.output_view.size())

    def writeln(self, s):
        self.write(s + "\n")

    def flush(self):
        pass

    def show(self):
        self.window.run_command("show_panel", {"panel": "output." + self.name})

    def close(self):
        self.closed = True
        pass
