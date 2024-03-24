import sublime

from unittest import TestCase
from ..core import DeferrableTestCase

__all__ = [
    "DeferrableViewTestCase",
    "ViewTestCase",
]


class ViewTestCaseMixin:
    view_settings = {
        "detect_indentation": False,
        "translate_tabs_to_spaces": False,
        "word_wrap": False,
    }

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()

        # make sure we have a window to work with
        settings = sublime.load_settings("Preferences.sublime-settings")
        self._orig_close_empty_window = settings.get("close_windows_when_empty")
        if self._orig_close_empty_window:
            settings.set("close_windows_when_empty", False)

        # apply pre-defined settings
        settings = self.view.settings()
        default_settings = getattr(self.__class__, "view_settings", {})
        for key, value in default_settings.items():
            settings.set(key, value)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.close()

        # restore original settings
        settings = sublime.load_settings("Preferences.sublime-settings")
        if self._orig_close_empty_window:
            settings.set("close_windows_when_empty", self._orig_close_empty_window)
            self._orig_close_empty_window = False

    def addCaretAt(self, row, col):
        """
        Add caret to given point (row, col).

        :param row:  The 0-based row number specifying target caret position.
        :param col:  The 0-based column number specifying target caret position.
        """
        self.view.sel().add(self.textPoint(row, col))

    def setCaretTo(self, row, col):
        """
        Move caret to given position (row, col).

        :param row:  The 0-based row number specifying target caret position.
        :param col:  The 0-based column number specifying target caret position.
        """
        self.view.sel().clear()
        self.view.sel().add(self.textPoint(row, col))

    def textPoint(self, row, col):
        """
        Return textpoint for given row,col coordinats.

        This method is an alias for ``self.view.text_point(row, col)``.

        :param row:  The 0-based row number.
        :param col:  The 0-based column number.

        :returns: Integer value of text point, belowing to row,col combination.
        """
        return self.view.text_point(row, col)

    def getRowText(self, row):
        """
        Return given row's content text.

        :param row: The row to return contents for.

        :return: unicode string with content of given row.
        """
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def getText(self):
        """Return view's content text."""
        return self.view.substr(sublime.Region(0, self.view.size()))

    def setText(self, text):
        """
        Set whole view's content, replacing anything existing.

        :param text: The text to replace the view's content with.
        """
        self.clearText()
        self.insertText(text)

    def clearText(self):
        """Clear whole view's content."""
        self.view.run_command("select_all")
        self.view.run_command("right_delete")

    def insertText(self, text):
        """
        Insert text at current position.

        :param text: The text to insert at current caret position.
        """
        self.view.run_command("insert", {"characters": text})

    def assertCaretAt(self, row, col):
        """
        Assert caret to be located at a certain position.

        :param row:  The 0-based row number.
        :param col:  The 0-based column number.
        """
        self.assertEqual(self.view.sel()[0].begin(), self.textPoint(row, col))

    def assertRowContentsEqual(self, row, text):
        """
        Expect given row's content to match ``text``.

        :param row:  The 0-based row number.
        :param col:  The 0-based column number.
        :param text: The expected content of given row.
        """
        self.assertEqual(self.getRowText(row), text)

    def assertViewContentsEqual(self, text):
        """
        Expect view's content to match ``text``.

        :param text: The expected content of the view.
        """
        self.assertEqual(self.getText(), text)


class ViewTestCase(ViewTestCaseMixin, TestCase):
    """
    This class describes a  view test case.

    This class provides infrastructure to run unit tests on dedicated ``sublime.View()`` objects.

    A new ``view`` object is created within the active ``window`` for each ``ViewTestCase``.

    The view is accessible via ``self.view`` from within each test method.

    The owning window can be accessed via ``self.window``.

    ```py
    class MyTestCase(ViewTestCase):
        # settings to apply to the created view
        view_settings = {
            "detect_indentation": False,
            "tab_size": 4,
            "translate_tabs_to_spaces": False,
            "word_wrap": False,
        }

        def test_editing(self):
            self.setText("foo")
            self.setCaretTo(0, 0)
            self.assertRowContentsEqual(0, "foofoo")
    ```
    """

    pass


class DeferrableViewTestCase(ViewTestCaseMixin, DeferrableTestCase):
    """
    This class describes a deferrable view test case.

    This class provides infrastructure to run unit tests on dedicated ``sublime.View()`` objects,
    which includes catching asynchronous events.

    A new ``view`` object is created within the active ``window`` for each ``ViewTestCase``.

    The view is accessible via ``self.view`` from within each test method.

    The owning window can be accessed via ``self.window``.

    ```py
    class MyTestCase(DeferrableViewTestCase):
        # settings to apply to the created view
        view_settings = {
            "detect_indentation": False,
            "tab_size": 4,
            "translate_tabs_to_spaces": False,
            "word_wrap": False,
        }

        def test_editing(self):
            self.setText("foo")
            self.setCaretTo(0, 0)
            self.defer(100, self.insertText, "foo")
            yield 200
            self.assertRowContentsEqual(0, "foofoo")
    ```
    """

    pass
