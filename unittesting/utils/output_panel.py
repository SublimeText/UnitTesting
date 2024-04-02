import collections
import os
import threading


class OutputPanel:
    def __init__(
        self,
        window,
        name,
        file_regex="",
        line_regex="",
        base_dir=None,
        word_wrap=False,
        line_numbers=False,
        gutter=False,
        scroll_past_end=False,
    ):
        self.name = name
        self.window = window
        self.output_view = window.create_output_panel(name)

        # default to the current file directory
        if not base_dir:
            view = window.active_view()
            if view:
                file_name = view.file_name()
                if file_name:
                    base_dir = os.path.dirname(file_name)

        settings = self.output_view.settings()
        settings.set("result_file_regex", file_regex)
        settings.set("result_line_regex", line_regex)
        settings.set("result_base_dir", base_dir)
        settings.set("word_wrap", word_wrap)
        settings.set("line_numbers", line_numbers)
        settings.set("gutter", gutter)
        settings.set("scroll_past_end", scroll_past_end)

        # make sure to apply settings
        self.output_view = window.create_output_panel(name)
        self.output_view.assign_syntax("unit-testing-test-result.sublime-syntax")
        self.output_view.set_read_only(True)
        self.closed = False

        self.text_queue_lock = threading.Lock()
        self.text_queue = collections.deque()

    def write(self, s):
        with self.text_queue_lock:
            self.text_queue.append(s)

    def writeln(self, s):
        self.write(s + "\n")

    def _write(self):
        text = ""
        with self.text_queue_lock:
            while self.text_queue:
                text += self.text_queue.popleft()

        self.output_view.run_command("append", {"characters": text, "force": True})
        self.output_view.show(self.output_view.size())

    def flush(self):
        self._write()

    def show(self):
        self.window.run_command("show_panel", {"panel": "output." + self.name})

    def close(self):
        self.flush()
        self.closed = True
