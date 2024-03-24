import sublime

from unittesting import DeferrableViewTestCase


class TestViewTestCase(DeferrableViewTestCase):

    def test_window_object(self):
        self.assertIsInstance(self.window, sublime.Window)

    def test_view_object(self):
        self.assertIsInstance(self.view, sublime.View)
        self.assertTrue(self.view.is_valid())

    def test_view_settings(self):
        for key, value in self.view_settings.items():
            self.assertEqual(self.view.settings().get(key), value)

    def test_clear_text_equal(self):
        self.clearText()
        yield 10
        self.assertViewContentsEqual("")

    def test_assert_view_content_equal(self):
        text = "hello world\ni am here"
        self.setText(text)
        yield 10
        self.assertViewContentsEqual(text)

    def test_assert_row_content_equal(self):
        self.setText("hello world\ni am here")
        yield 10
        self.assertRowContentsEqual(0, "hello world")
        self.assertRowContentsEqual(1, "i am here")

    def test_assert_caret_at(self):
        self.setText("hello world")
        yield 10
        self.setCaretTo(0, 5)
        yield 10
        self.assertCaretAt(0, 5)

    def test_assert_carets_at(self):
        self.setText("hello world")
        yield 10
        self.setCaretTo(0, 5)
        yield 10
        self.addCaretAt(0, 10)
        yield 10
        self.assertCaretsAt(((0, 5), (0, 10)))
