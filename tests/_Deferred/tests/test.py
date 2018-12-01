import sublime
from unittest import TestCase  # FIXME Import unused? # noqa: F401
from unittesting import DeferrableTestCase


class TestDeferrable(DeferrableTestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()
        # make sure we have a window to work with
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def setText(self, string):
        self.view.run_command("insert", {"characters": string})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def test_defer(self):
        self.setText("foo")
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(0, 0))
        sublime.set_timeout(lambda: self.setText("foo"), 100)
        yield 200
        self.assertEqual(self.getRow(0), "foofoo")

    def test_condition(self):
        x = []

        def append():
            x.append(1)

        def condition():
            return len(x) == 1

        sublime.set_timeout(append, 100)

        # wait until `condition()` is true
        yield condition

        self.assertEqual(x[0], 1)
