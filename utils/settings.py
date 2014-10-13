
# Copyright (C) 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software

import sublime


def get(key, default=None):
    """Get a setting value from the global config or project config if exists

    If it doesn't exists, returns the given default (if any)
    """

    settings = {}
    project_data = sublime.active_window().project_data()
    if project_data is not None:
        settings = project_data.get('settings')

    plugin_settings = sublime.load_settings('UnitTesting.sublime-settings')
    return settings.get(key, plugin_settings.get(key, default))
