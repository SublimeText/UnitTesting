import sublime
version = sublime.version()

__all__ = ["Jfile"]

if version >= '3000':
    from .jfile import Jfile
else:
    from jfile import Jfile
