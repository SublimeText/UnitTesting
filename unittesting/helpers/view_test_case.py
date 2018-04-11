import sublime

from unittest import TestCase


class ViewTestCase(TestCase):
    def setUp(self):
        self.view = sublime.active_window().new_file()

        settings = self.view.settings()
        default_settings = getattr(self.__class__, 'view_settings', {})
        for key, value in default_settings.items():
            settings.set(key, value)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def _viewContents(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

    def assertViewContentsEqual(self, text):
        self.assertEqual(self._viewContents(), text)
