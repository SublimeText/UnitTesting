import os
import json
import shutil
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
            on_change_key = settings_file_name + "catch_on_change"
            caught = [False]
            s.add_on_change(on_change_key, lambda: caught.__setitem__(0, True))

            if os.path.exists(settings_path):
                shutil.move(settings_path, new_settings_path)
                yield lambda: caught[0]
                yield 500

            caught = [False]
            with open(settings_path, "w") as f:
                f.write(json.dumps(settings))
            yield lambda: caught[0]
            yield 500
            s.clear_on_change(on_change_key)

        deferred = super().setUpClass()
        if isinstance(deferred, DeferrableMethod):
            yield from deferred

    @classmethod
    def tearDownClass(cls):
        for settings_file_name, settings in cls.override_preferences.items():
            settings_path = os.path.join(sublime.packages_path(), "User", settings_file_name)
            new_settings_path = settings_path + ".bak"
            if os.path.exists(new_settings_path):
                shutil.move(new_settings_path, settings_path)
            else:
                try:
                    os.unlink(settings_path)
                except Exception:
                    pass

        deferred = super().tearDownClass()
        if isinstance(deferred, DeferrableMethod):
            yield from deferred
