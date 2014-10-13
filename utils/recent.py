import sublime

recent_package_file = "UnitTesting.recent-package"

def get():
    recent_package_settings = sublime.load_settings(recent_package_file)
    return recent_package_settings.get("recent_package", "Package Name")

def set(name):
    recent_package_settings = sublime.load_settings(recent_package_file)
    recent_package_settings.get("recent_package", name)
    sublime.save_settings(recent_package_file)
