import sublime

version = sublime.version()

if version >= "3000":
    from .unittesting import *
else:
    from unittesting import *
