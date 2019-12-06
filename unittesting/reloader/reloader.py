import sublime
import sublime_plugin
import os
import os.path
import posixpath
import threading
import sys

from .dprint import dprint
from .importer import ReloadingImporter
from .resolver import resolve_parents


def get_package_modules(package_names):
    package_names = set(package_names)
    package_path_bases = [
        p
        for pkg_name in package_names
        for p in (
            os.path.join(
                sublime.installed_packages_path(),
                pkg_name + '.sublime-package'
            ),
            os.path.join(sublime.packages_path(), pkg_name),
        )
    ]

    def module_paths(module):
        try:
            yield module.__file__
        except AttributeError:
            pass

        try:
            yield from module.__path__
        except AttributeError:
            pass

    for module in sys.modules.values():
        try:
            base, path = next(
                (base, path)
                for path in module_paths(module)
                for base in package_path_bases
                if path and (path == base or path.startswith(base + os.sep))
            )
        except StopIteration:
            continue
        else:
            is_plugin = (os.path.dirname(path) == base)
            yield module.__name__, is_plugin

    # get all the top level plugins in case they were removed from sys.modules
    for path in sublime.find_resources("*.py"):
        for pkg_name in package_names:
            if posixpath.dirname(path) == 'Packages/'+pkg_name:
                yield pkg_name + '.' + posixpath.basename(posixpath.splitext(path)[0]), True


def reload_package(pkg_name, dummy=True, verbose=True):
    zipped_file = os.path.join(
        sublime.installed_packages_path(), "{}.sublime-package".format(pkg_name))
    unzipped_folder = os.path.join(sublime.packages_path(), pkg_name)
    if not os.path.exists(zipped_file) and not os.path.exists(unzipped_folder):
        dprint("error:", pkg_name, "is not installed.")
        return
    if verbose:
        dprint("begin", fill='=')

    parents = list(resolve_parents(pkg_name))

    modules = sorted(
        list(set(get_package_modules([pkg_name] + parents))),
        key=lambda x: x[0].split('.')
    )

    plugins = [m for m, is_plugin in modules if is_plugin]
    # Tell Sublime to unload plugin_modules
    for plugin in plugins:
        if plugin in sys.modules:
            sublime_plugin.unload_module(sys.modules[plugin])

    # these are modules marked to be reloaded, they are not necessarily reloaded
    modules_to_reload = [sys.modules[m] for m, is_plugin in modules if m in sys.modules]

    with ReloadingImporter(modules_to_reload, verbose) as importer:
        if plugins:
            # we only reload top level plugin_modules to mimic Sublime Text natural order
            for plugin in plugins:
                if plugin in sys.modules:
                    module = sys.modules[plugin]
                    importer.reload(module)

            for plugin in plugins:
                if plugin in sys.modules:
                    module = sys.modules[plugin]
                    sublime_plugin.load_module(module)
                else:
                    # in case we missed something
                    sublime_plugin.reload_plugin(plugin)
        else:
            # it is possibly a dependency but no packages use it
            for module in modules_to_reload:
                importer.reload(module)

    if dummy:
        load_dummy(verbose)

    if verbose:
        dprint("end", fill='-')


def load_dummy(verbose):
    """
    Hack to trigger automatic "reloading plugins".

    This is needed to ensure TextCommand's and WindowCommand's are ready.
    """
    if verbose:
        dprint("installing dummy package")

    if sys.version_info >= (3, 8):
        # in ST 4, User package is always loaded in python 3.8
        dummy_name = "User._dummy"
        dummy_py = os.path.join(sublime.packages_path(), "User", "_dummy.py")
    else:
        # in ST 4, packages under Packages are always loaded in python 3.3
        dummy_name = "_dummy"
        dummy_py = os.path.join(sublime.packages_path(), "_dummy.py")

    with open(dummy_py, "w"):
        pass

    def remove_dummy(trial=0):
        if dummy_name in sys.modules:
            if verbose:
                dprint("removing dummy package")
            try:
                os.unlink(dummy_py)
            except FileNotFoundError:
                pass
            after_remove_dummy()
        elif trial < 300:
            threading.Timer(0.1, lambda: remove_dummy(trial + 1)).start()
        else:
            try:
                os.unlink(dummy_py)
            except FileNotFoundError:
                pass

    condition = threading.Condition()

    def after_remove_dummy(trial=0):
        if dummy_name not in sys.modules:
            condition.acquire()
            condition.notify()
            condition.release()
        elif trial < 300:
            threading.Timer(0.1, lambda: after_remove_dummy(trial + 1)).start()

    threading.Timer(0.1, remove_dummy).start()
    condition.acquire()
    condition.wait(30)  # 30 seconds should be enough for all regular usages
    condition.release()
