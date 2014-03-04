# example
import sublime, sublime_plugin

class HelloWorldCommand(sublime_plugin.TextCommand):
    def run(self,edit):
        view = self.view
        view.insert(edit, 0, "hello world")