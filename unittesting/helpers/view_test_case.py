import sublime

from unittest import TestCase
from ..core import DeferrableTestCase

__all__ = [
    "DeferrableViewTestCase",
    "ViewTestCase",
]


class ViewTestCaseMixin:
    def setUp(self):
        self.view = sublime.active_window().new_file()

        # make sure we have a window to work with
        settings = sublime.load_settings("Preferences.sublime-settings")
        settings.set("close_windows_when_empty", False)

        settings = self.view.settings()
        default_settings = getattr(self.__class__, "view_settings", {})
        for key, value in default_settings.items():
            settings.set(key, value)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.close()

    def addCaretAt(self, row, col):
        """Add caret to given point (row, col)."""
        self.view.sel().add(self.textPoint(row, col))

    def setCaretTo(self, row, col):
        """Move caret to given point (row, col)."""
        self.view.sel().clear()
        self.view.sel().add(self.textPoint(row, col))

    def textPoint(self, row, col):
        """Return textpoint for given row,col coordinats."""
        return self.view.text_point(row, col)

    def getRowText(self, row):
        """Return given row's content text."""
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def getText(self):
        """Return view's content text."""
        return self.view.substr(sublime.Region(0, self.view.size()))

    def setText(self, text):
        """Set whole view's content, replacing anything existing."""
        self.clearText()
        self.insertText(text)

    def clearText(self):
        """Clear whole view's content."""
        self.view.run_command("select_all")
        self.view.run_command("right_delete")

    def insertText(self, text):
        """Insert text at current position."""
        self.view.run_command("insert", {"characters": text})

    def assertViewContentsEqual(self, text):
        self.assertEqual(self.getText(), text)



class ViewTestCase(ViewTestCaseMixin, TestCase):
    pass


class DeferrableViewTestCase(ViewTestCaseMixin, DeferrableTestCase):
    pass
