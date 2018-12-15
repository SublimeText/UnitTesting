import sublime
import sublime_plugin
import os
import threading
import builtins
import functools
import importlib
import sys
import types
from contextlib import contextmanager
from .stack_meter import StackMeter


try:
    from package_control.package_manager import PackageManager

    def is_dependency(pkg_name):
        return PackageManager()._is_dependency(pkg_name)

except ImportError:
    def is_dependency(pkg_name):
        return False


def dprint(*args, fill=None, fill_width=60, **kwargs):
    if fill is not None:
        sep = str(kwargs.get('sep', ' '))
        caption = sep.join(args)
        args = "{0:{fill}<{width}}".format(caption and caption + sep,
                                           fill=fill, width=fill_width),
    print("[Package Reloader]", *args, **kwargs)


def path_contains(a, b):
    return a == b or b.startswith(a + os.sep)


def get_package_modules(pkg_name):
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
        file = getattr(module, '__file__', '')
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


# check the link for comments
# https://github.com/divmain/GitSavvy/blob/599ba3cdb539875568a96a53fafb033b01708a67/common/util/reload.py
def reload_package(pkg_name, dummy=True, verbose=True):
    if is_dependency(pkg_name):
        reload_dependency(pkg_name, dummy, verbose)
        return

    if pkg_name not in sys.modules:
        dprint("error:", pkg_name, "is not loaded.")
        return

    if verbose:
        dprint("begin", fill='=')

    modules = get_package_modules(pkg_name)

    for m in modules:
        if m in sys.modules:
            sublime_plugin.unload_module(modules[m])
            del sys.modules[m]

    try:
        with intercepting_imports(modules, verbose), \
                importing_fromlist_aggresively(modules):

            reload_plugin(pkg_name)
    except Exception:
        dprint("reload failed.", fill='-')
        reload_missing(modules, verbose)
        raise

    if dummy:
        load_dummy(verbose)

    if verbose:
        dprint("end", fill='-')


def reload_dependency(dependency_name, dummy=True, verbose=True):
    """
    Package Control dependencies aren't regular packages, so we don't want to
    call `sublime_plugin.unload_module` or `sublime_plugin.reload_plugin`.
    Instead, we manually unload all of the modules in the dependency and then
    `reload_package` any packages that use that dependency. (We have to manually
    unload the dependency's modules because calling `reload_package` on a
    dependent module will not unload the dependency.)
    """
    for name in get_package_modules(dependency_name):
        del sys.modules[name]

    manager = PackageManager()
    for package in manager.list_packages():
        if dependency_name in manager.get_dependencies(package):
            reload_package(package, dummy=False, verbose=verbose)

    if dummy:
        load_dummy(verbose)


def load_dummy(verbose):
    """
    Hack to trigger automatic "reloading plugins".

    This is needed to ensure TextCommand's and WindowCommand's are ready.
    """
    if verbose:
        dprint("installing dummy package")
    dummy = "_dummy_package"
    dummy_py = os.path.join(sublime.packages_path(), "%s.py" % dummy)
    with open(dummy_py, "w"):
        pass

    def remove_dummy(trial=0):
        if dummy in sys.modules:
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
        if dummy not in sys.modules:
            condition.acquire()
            condition.notify()
            condition.release()
        elif trial < 300:
            threading.Timer(0.1, lambda: after_remove_dummy(trial + 1)).start()

    threading.Timer(0.1, remove_dummy).start()
    condition.acquire()
    condition.wait(30)  # 30 seconds should be enough for all regular usages
    condition.release()


def reload_missing(modules, verbose):
    missing_modules = {name: module for name, module in modules.items()
                       if name not in sys.modules}
    if missing_modules:
        if verbose:
            dprint("reload missing modules")
        for name in missing_modules:
            if verbose:
                dprint("reloading missing module", name)
            sys.modules[name] = modules[name]


def reload_plugin(pkg_name):
    pkg_path = os.path.join(os.path.realpath(sublime.packages_path()), pkg_name)
    plugins = [pkg_name + "." + os.path.splitext(file_path)[0]
               for file_path in os.listdir(pkg_path) if file_path.endswith(".py")]
    for plugin in plugins:
        sublime_plugin.reload_plugin(plugin)


@contextmanager
def intercepting_imports(modules, verbose):
    finder = FilterFinder(modules, verbose)
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        if finder in sys.meta_path:
            sys.meta_path.remove(finder)


@contextmanager
def importing_fromlist_aggresively(modules):
    orig___import__ = builtins.__import__

    @functools.wraps(orig___import__)
    def __import__(name, globals=None, locals=None, fromlist=(), level=0):
        module = orig___import__(name, globals, locals, fromlist, level)
        if fromlist and module.__name__ in modules:
            if '*' in fromlist:
                fromlist = list(fromlist)
                fromlist.remove('*')
                fromlist.extend(getattr(module, '__all__', []))
            for x in fromlist:
                if isinstance(getattr(module, x, None), types.ModuleType):
                    from_name = '{}.{}'.format(module.__name__, x)
                    if from_name in modules:
                        importlib.import_module(from_name)
        return module

    builtins.__import__ = __import__
    try:
        yield
    finally:
        builtins.__import__ = orig___import__


class FilterFinder:
    def __init__(self, modules, verbose):
        self._modules = modules
        self._stack_meter = StackMeter()
        self._verbose = verbose

    def find_module(self, name, path=None):
        if name in self._modules:
            return self

    def load_module(self, name):
        module = self._modules[name]
        sys.modules[name] = module  # restore the module back
        with self._stack_meter as depth:
            if self._verbose:
                dprint("reloading", ('| ' * depth) + '|--', name)
            try:
                return module.__loader__.load_module(name)
            except Exception:
                if name in sys.modules:
                    del sys.modules[name]  # to indicate an error
                raise
