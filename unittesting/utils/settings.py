import sublime

settings_file = "UnitTesting.sublime-settings"


def get(var, default):
    s = sublime.load_settings(settings_file)
    return s.get(var, default)


def set(var, name):
    s = sublime.load_settings(settings_file)
    s.set(var, name)
    sublime.save_settings(settings_file)
