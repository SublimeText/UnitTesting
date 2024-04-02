import os
import sublime

from unittesting import OverridePreferencesTestCase


class PreferencesTestCase(OverridePreferencesTestCase):
    SETTINGS_FILE = "_UnitTestingTest.sublime-settings"
    SETTINGS_PATH = os.path.join(sublime.packages_path(), "User", SETTINGS_FILE)

    override_preferences = {
        SETTINGS_FILE: {
            "enable": True,
            "list": ["one", "two", "three"]
        }
    }

    @classmethod
    def setUpClass(cls):
        settings = sublime.load_settings(cls.SETTINGS_FILE)
        settings.set("enable", False)
        settings.set("list", ["foo"])
        sublime.save_settings(cls.SETTINGS_FILE)
        yield 500  # give ST some time to load initial settings file
        yield from super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        yield from super().tearDownClass()
        os.remove(cls.SETTINGS_PATH)

    def test_backup_exists(self):
        self.assertTrue(os.path.isfile(self.SETTINGS_PATH + ".bak"))

    def test_override_exists(self):
        self.assertTrue(os.path.isfile(self.SETTINGS_PATH))

    def test_enabled(self):
        settings = sublime.load_settings(self.SETTINGS_FILE)
        self.assertTrue(settings.get("enable"))

    def test_list_setting(self):
        settings = sublime.load_settings(self.SETTINGS_FILE)
        self.assertEqual(
            self.override_preferences[self.SETTINGS_FILE]["list"],
            settings.get("list")
        )
