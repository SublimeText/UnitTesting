import os
import sublime

from .utils import JsonFile


class Unit:

    def __init__(self, s):
        self.package = s['package']

        self.output = s.get('output', None)
        self.syntax_test = s.get('syntax_test', False)
        self.syntax_compatibility = s.get('syntax_compatibility', False)
        self.color_scheme_test = s.get('color_scheme_test', False)
        self.coverage = s.get('coverage', False)

    def run(self):
        if self.syntax_test:
            sublime.run_command("unit_testing_syntax", {
                "package": self.package,
                "output": self.output
            })
        elif self.syntax_compatibility:
            sublime.run_command("unit_testing_syntax_compatibility", {
                "package": self.package,
                "output": self.output
            })
        elif self.color_scheme_test:
            sublime.run_command("unit_testing_color_scheme", {
                "package": self.package,
                "output": self.output
            })
        elif self.coverage:
            sublime.run_command("unit_testing_coverage", {
                "package": self.package,
                "output": self.output,
                "generate_xml_report": True
            })
        else:
            sublime.run_command("unit_testing", {
                "package": self.package,
                "output": self.output
            })


class Scheduler:

    def __init__(self):
        self.units = []
        self.j = JsonFile(os.path.join(
            sublime.packages_path(),
            'User', 'UnitTesting',
            'schedule.json')
        )

    def load_schedule(self):
        self.schedule = self.j.load()
        for s in self.schedule:
            self.units.append(Unit(s))

    def run(self):
        self.load_schedule()
        for u in self.units:
            u.run()
        self.clean_schedule()

    def clean_schedule(self):
        self.j.save([])


def run_scheduler():
    # delay schedule initialization and execution
    sublime.set_timeout(lambda: Scheduler().run(), 2000)
