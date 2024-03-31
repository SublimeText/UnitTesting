import os
import sublime

from ..core import DeferrableMethod
from ..core import DeferrableTestCase


class OverridePreferencesTestCase(DeferrableTestCase):
    override_preferences = {}

    @classmethod
    def setUpClass(cls):
        for settings_file_name, settings in cls.override_preferences.items():
            settings_path = os.path.join(sublime.packages_path(), "User", settings_file_name)
            new_settings_path = settings_path + ".bak"

            s = sublime.load_settings(settings_file_name)
            on_change_key = settings_file_name + ".catch_on_change"
            caught = [False]
            s.add_on_change(on_change_key, lambda: caught.__setitem__(0, True))
            try:
                try:
                    os.remove(new_settings_path)
                except FileNotFoundError:
                    pass
                try:
                    os.rename(settings_path, new_settings_path)
                except FileNotFoundError:
                    pass
                yield lambda: caught[0]
                caught = [False]
                with open(settings_path, "w", encoding="utf-8") as f:
                    f.write(sublime.encode_value(settings, True))
                yield lambda: caught[0]
            finally:
                s.clear_on_change(on_change_key)

        deferred = super().setUpClass()
        if isinstance(deferred, DeferrableMethod):
            yield from deferred

    @classmethod
    def tearDownClass(cls):
        for settings_file_name in cls.override_preferences:
            settings_path = os.path.join(sublime.packages_path(), "User", settings_file_name)
            new_settings_path = settings_path + ".bak"
            try:
                os.remove(settings_path)
            except FileNotFoundError:
                pass
            try:
                os.rename(new_settings_path, settings_path)
            except FileNotFoundError:
                pass

        deferred = super().tearDownClass()
        if isinstance(deferred, DeferrableMethod):
            yield from deferred
