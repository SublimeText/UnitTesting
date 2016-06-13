import os
import codecs
import sublime
import json


class JsonFile:

    def __init__(self, fpath, encoding="utf-8"):
        self.encoding = encoding
        self.fpath = fpath

    def load(self, default=[]):
        self.fdir = os.path.dirname(self.fpath)
        if not os.path.isdir(self.fdir):
            os.makedirs(self.fdir)
        if os.path.exists(self.fpath):
            f = codecs.open(self.fpath, "r+", encoding=self.encoding)
            try:
                if sublime.version() > "3000":
                    content = f.read()
                    data = sublime.decode_value(content)
                else:
                    data = json.load(f)
            except:
                print("%s is bad!" % self.fpath)
                f.close()
                raise
            if not data:
                data = default
            f.close()
        else:
            f = codecs.open(self.fpath, "w+", encoding=self.encoding)
            data = default
            f.close()
        return data

    def save(self, data, indent=4):
        self.fdir = os.path.dirname(self.fpath)
        if not os.path.isdir(self.fdir):
            os.makedirs(self.fdir)
        f = codecs.open(self.fpath, "w+", encoding=self.encoding)
        if sublime.version() > "3000":
            f.write(sublime.encode_value(data, True))
        else:
            f.write(json.dumps(data, ensure_ascii=False, indent=indent))
        f.close()

    def remove(self):
        if os.path.exists(self.fpath):
            os.remove(self.fpath)
