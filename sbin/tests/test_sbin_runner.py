import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


RUNNER_PATH = Path(__file__).resolve().parents[1] / "run_tests.py"
SPEC = importlib.util.spec_from_file_location("sbin_run_tests", RUNNER_PATH)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def options(**overrides):
    values = {
        "color_scheme_test": False,
        "coverage": False,
        "fail_if_no_resources": True,
        "failfast": False,
        "pattern": None,
        "reload_package_on_testing": False,
        "syntax_compatibility": False,
        "syntax_test": False,
        "tests_dir": None,
        "unit_test": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class BuildSchedulesTests(unittest.TestCase):
    def test_defaults_to_unit_tests(self):
        self.assertEqual(
            runner.build_named_schedules(options(), "Example"),
            [
                (
                    "unit tests",
                    {
                        "package": "Example",
                        "coverage": False,
                        "reload_package_on_testing": False,
                    },
                )
            ],
        )

    def test_builds_synchronous_categories_before_unit_tests(self):
        schedules = runner.build_named_schedules(
            options(
                unit_test=True,
                syntax_test=True,
                syntax_compatibility=True,
                fail_if_no_resources=False,
                pattern="selected*",
                tests_dir="syntax/test",
            ),
            "Example",
        )

        self.assertEqual(
            [name for name, _ in schedules],
            ["syntax tests", "syntax compatibility checks", "unit tests"],
        )
        for _, schedule in schedules:
            self.assertEqual(schedule["pattern"], "selected*")
            self.assertEqual(schedule["tests_dir"], "syntax/test")
            self.assertFalse(schedule["fail_if_no_resources"])

    def test_assigns_distinct_outputs_to_multiple_schedules(self):
        schedules = runner.build_named_schedules(
            options(unit_test=True, syntax_test=True), "Example"
        )

        output_files = runner.configure_schedule_outputs(schedules, "/output")

        self.assertEqual(
            output_files,
            [
                ("syntax tests", os.path.join("/output", "result-syntax-tests")),
                ("unit tests", os.path.join("/output", "result-unit-tests")),
            ],
        )


class OutputTests(unittest.TestCase):
    def test_wait_heading_ends_with_newline_when_output_already_exists(self):
        with tempfile.NamedTemporaryFile() as output:
            output.write(b"ready")
            output.flush()
            rendered = io.StringIO()
            with redirect_stdout(rendered):
                print("Wait for output...", end="")
                runner.wait_for_output(output.name, "unused")

        self.assertEqual(rendered.getvalue(), "Wait for output...\n")

    def test_can_hide_category_done_message(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as output:
            output.write("OK\n\n" + runner.DONE_MESSAGE)
            output_path = output.name

        try:
            rendered = io.StringIO()
            with redirect_stdout(rendered):
                success = runner.read_output(
                    output_path, color="never", show_done=False
                )
        finally:
            Path(output_path).unlink()

        self.assertTrue(success)
        self.assertEqual(rendered.getvalue(), "OK\n\n")


class CreateSchedulesTests(unittest.TestCase):
    def test_replaces_package_with_every_selected_schedule(self):
        schedules = runner.build_named_schedules(
            options(unit_test=True, syntax_test=True), "Example"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            schedule_file = Path(temp_dir) / "schedule.json"
            schedule_file.write_text(
                json.dumps(
                    [
                        {"package": "Other"},
                        {"package": "Example", "stale": True},
                    ]
                )
            )
            with mock.patch.object(runner, "SCHEDULE_FILE_PATH", str(schedule_file)):
                with redirect_stdout(io.StringIO()):
                    runner.create_schedules("Example", schedules)
            saved = json.loads(schedule_file.read_text())

        self.assertEqual(saved[0], {"package": "Other"})
        self.assertEqual(saved[1:], [schedule for _, schedule in schedules])


if __name__ == "__main__":
    unittest.main()
