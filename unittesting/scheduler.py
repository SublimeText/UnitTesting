import os
import sublime

__all__ = ["run_scheduler"]


class Scheduler:
    def run(self):
        schedule = Schedule(
            os.path.join(
                sublime.packages_path(), "User", "UnitTesting", "schedule.json"
            )
        )
        for s in schedule.load():
            Unit(s).run()
        schedule.save([])


class Schedule:
    def __init__(self, fpath, encoding="utf-8"):
        self.encoding = encoding
        self.fpath = fpath

    def load(self, default=[]):
        try:
            with open(self.fpath, "r", encoding=self.encoding) as fp:
                json_data = sublime.decode_value(fp.read())
                if not isinstance(json_data, list):
                    raise ValueError("Unsupported data format!")
                return json_data
        except FileNotFoundError:
            return default
        except Exception as e:
            print("Error loading {}: {!s}".format(self.fpath, e))
            return default

    def save(self, data, indent=4):
        self.fdir = os.path.dirname(self.fpath)
        os.makedirs(self.fdir, exist_ok=True)
        with open(self.fpath, "w", encoding=self.encoding) as fp:
            fp.write(sublime.encode_value(data, True))


class Unit:
    def __init__(self, s):
        self.package = s["package"]

        self.output = s.get("output", None)
        self.syntax_test = s.get("syntax_test", False)
        self.syntax_compatibility = s.get("syntax_compatibility", False)
        self.color_scheme_test = s.get("color_scheme_test", False)
        self.coverage = s.get("coverage", False)

    def run(self):
        if self.color_scheme_test:
            sublime.active_window().run_command(
                "unit_testing_color_scheme",
                {"package": self.package, "output": self.output},
            )
        elif self.syntax_test:
            sublime.active_window().run_command(
                "unit_testing_syntax", {"package": self.package, "output": self.output}
            )
        elif self.syntax_compatibility:
            sublime.active_window().run_command(
                "unit_testing_syntax_compatibility",
                {"package": self.package, "output": self.output},
            )
        else:
            sublime.active_window().run_command(
                "unit_testing",
                {
                    "package": self.package,
                    "output": self.output,
                    "coverage": self.coverage,
                    "generate_xml_report": True,
                },
            )


def run_scheduler():
    # delay schedule initialization and execution
    sublime.set_timeout(lambda: Scheduler().run(), 2000)
