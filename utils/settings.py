
# Copyright (C) 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software

import sublime


def get(view, key, default=None):
    """Get a setting value from the global config or project config if exists

    If it doesn't exists, returns the given default (if any)
    """

    if view is None:
        return None

    plugin_settings = sublime.load_settings('UnitTesting.sublime-settings')
    return view.settings().get(key, plugin_settings.get(key, default))
