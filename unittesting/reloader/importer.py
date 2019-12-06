import builtins
import imp
from inspect import ismodule

from .stack_meter import StackMeter
from .dprint import dprint


class ReloadingImporter():
    def __init__(self, modules, verbose):
        self._modules_to_reload = set(modules)
        self._stack_meter = StackMeter()
        self._verbose = verbose

    def reload(self, module):
        try:
            self._modules_to_reload.remove(module)
        except KeyError:
            return

        with self._stack_meter as depth:
            if self._verbose:
                dprint("reloading", ('| ' * depth) + '|--', module.__name__)

            imp.reload(module)

    def __import__(self, name, globals=None, locals=None, fromlist=(), level=0):
        module = self._orig___import__(name, globals, locals, fromlist, level)

        self.reload(module)

        if fromlist:
            from_names = [
                name
                for item in fromlist
                for name in (
                    getattr(module, '__all__', []) if item == '*' else (item,)
                )
            ]

            for name in from_names:
                value = getattr(module, name, None)
                if ismodule(value):
                    self.reload(value)

        return module

    def __enter__(self):
        self._orig___import__ = __import__
        builtins.__import__ = self.__import__
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        builtins.__import__ = self._orig___import__
        del self._orig___import__
