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
    UNIT_TESTING_OPTION_KEYS = (
        "capture_console",
        "condition_timeout",
        "deferred",
        "failfast",
        "generate_html_report",
        "generate_xml_report",
        "pattern",
        "reload_package_on_testing",
        "tests_dir",
        "verbosity",
        "warnings",
    )

    def __init__(self, s):
        self.package = s["package"]

        self.output = s.get("output")
        self.syntax_test = s.get("syntax_test", False)
        self.syntax_compatibility = s.get("syntax_compatibility", False)
        self.color_scheme_test = s.get("color_scheme_test", False)
        self.coverage = s.get("coverage", False)
        self.unit_testing_options = {
            key: s[key] for key in self.UNIT_TESTING_OPTION_KEYS if key in s
        }

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
            sublime.active_window().run_command("unit_testing", self.unit_testing_args())

    def unit_testing_args(self):
        args = {
            "package": self.package,
            "output": self.output,
            "coverage": self.coverage,
            "generate_xml_report": True,
        }
        args.update(self.unit_testing_options)
        return args


def run_scheduler():
    # Delay schedule execution. In practice, a single queue tick (`0`) seems
    # sufficient once Sublime starts draining callbacks.
    try:
        delay = int(os.environ.get("UNITTESTING_SCHEDULER_DELAY_MS", "2000"))
    except ValueError:
        delay = 2000

    sublime.set_timeout(lambda: Scheduler().run(), delay)
