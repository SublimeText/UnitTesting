import os

import sublime


def open(window):
    switchable = _get_switchable(window)
    if switchable:
        window.open_file(switchable)


def _get_switchable(window):
    view = window.active_view()
    if not view:
        return

    file_name = view.file_name()
    if not file_name:
        return

    if not file_name.endswith('.py'):
        return

    # We need to evaluate the realpath of the file in order to mutate it to and
    # from test -> file and file -> test.
    file_name = os.path.realpath(file_name)

    for package in os.listdir(sublime.packages_path()):
        p_path = os.path.join(sublime.packages_path(), package)
        if file_name.startswith(p_path):
            if os.path.isdir(p_path):
                f_path, f_base = os.path.split(file_name)

                if f_base.startswith('test_'):
                    # Switch from test -> file
                    switch_to_file = os.path.join(
                        f_path.replace(os.path.join(p_path, 'tests'), os.path.join(p_path)),
                        f_base[5:])
                else:
                    # Switch from file -> test
                    switch_to_file = os.path.join(
                        f_path.replace(p_path, os.path.join(p_path, 'tests')),
                        'test_' + f_base)

                # Checks to see if the file we're switching to is already open,
                # and takes into account symlinks i.e. if we didn't do this then
                # we would end up opening a second view with the realpath file
                # rather than opening the symlinked one.
                for view in window.views():
                    if view.file_name():
                        if os.path.realpath(view.file_name()) == switch_to_file:
                            return view.file_name()

                if os.path.isfile(switch_to_file):
                    return switch_to_file
