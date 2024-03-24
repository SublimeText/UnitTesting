import functools
import importlib
import os
import posixpath
import sublime
import sublime_plugin
import sys
import threading


def dprint(*args, fill=None, fill_width=60, **kwargs):
    if fill is not None:
        sep = str(kwargs.get('sep', ' '))
        caption = sep.join(args)
        args = "{0:{fill}<{width}}".format(caption and caption + sep,
                                           fill=fill, width=fill_width),
    print("UnitTesting:", *args, **kwargs)


def path_contains(a, b):
    return a == b or b.startswith(a + os.sep)


def get_package_modules(pkg_name):
    # (str) -> Dict[str, ModuleType]
    in_installed_path = functools.partial(
        path_contains,
        os.path.join(
            sublime.installed_packages_path(),
            pkg_name + '.sublime-package'
        )
    )

    in_package_path = functools.partial(
        path_contains,
        os.path.join(sublime.packages_path(), pkg_name)
    )

    def module_in_package(module):
        # Other (extracted) ST plugins using python 3.8 have this set to
        # `None` surprisingly.
        file = getattr(module, '__file__', None) or ''
        paths = getattr(module, '__path__', ())
        return (
            in_installed_path(file) or any(map(in_installed_path, paths)) or
            in_package_path(file) or any(map(in_package_path, paths))
        )

    return {
        name: module
        for name, module in sys.modules.items()
        if module_in_package(module)
    }


def package_plugins(pkg_name):
    return [
        pkg_name + '.' + posixpath.basename(posixpath.splitext(path)[0])
        for path in sublime.find_resources("*.py")
        if posixpath.dirname(path) == 'Packages/' + pkg_name
    ]


def reload_package(pkg_name, dummy=True, verbose=True):
    if pkg_name not in sys.modules:
        dprint("error:", pkg_name, "is not loaded.")
        return

    all_modules = {
        module_name: module
        for module_name, module in get_package_modules(pkg_name).items()
    }
    plugins = [plugin for plugin in package_plugins(pkg_name)]

    # Tell Sublime to unload plugins
    for plugin in plugins:
        module = sys.modules.get(plugin)
        if module:
            sublime_plugin.unload_module(module)

    # Unload modules
    for module_name in all_modules:
        sys.modules.pop(module_name)

    sys.modules[pkg_name] = importlib.import_module(pkg_name)

    # After all (sub-)modules have been removed from modules cache,
    # reloading top-level plugins will automatically re-import them
    # in correct order without any further action needed.
    for plugin in plugins:
        sublime_plugin.reload_plugin(plugin)

    # Install and uninstall a dummy package so ST updates
    # command and event listener bindings
    if dummy:
        load_dummy(verbose)


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
