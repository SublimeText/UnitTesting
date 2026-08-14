import importlib.util
import io
import unittest
from contextlib import redirect_stderr
from pathlib import Path


RUNNER_PATH = Path(__file__).resolve().parents[1] / "run_tests.py"
SPEC = importlib.util.spec_from_file_location("docker_run_tests", RUNNER_PATH)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class ParseArgsTests(unittest.TestCase):
    def test_rejects_repeated_file(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            runner.parse_args(["--file", "a.py", "--file", "b.py"])

        self.assertEqual(error.exception.code, 2)

    def test_rejects_disabling_every_category(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            runner.parse_args(
                [
                    "--no-unit-tests",
                    "--no-syntax-tests",
                    "--no-syntax-compatibility-checks",
                ]
            )

        self.assertEqual(error.exception.code, 2)


class TestCategoryTests(unittest.TestCase):
    def test_runs_every_category_by_default(self):
        args = runner.parse_args([])

        self.assertEqual(
            runner.resolve_test_categories(args, None),
            runner.ALL_TEST_CATEGORIES,
        )

    def test_skips_disabled_categories(self):
        args = runner.parse_args(["--no-syntax-tests"])

        self.assertEqual(
            runner.resolve_test_categories(args, None),
            (runner.UNIT_TESTS, runner.SYNTAX_COMPATIBILITY_CHECKS),
        )

    def test_unit_discovery_options_select_unit_tests(self):
        args = runner.parse_args(["--tests-dir", "specs", "--pattern", "spec*.py"])

        self.assertEqual(
            runner.resolve_test_categories(args, None),
            (runner.UNIT_TESTS,),
        )

    def test_infers_category_from_file(self):
        args = runner.parse_args([])
        cases = {
            "tests/test_example.py": runner.UNIT_TESTS,
            "syntax/syntax_test_example": runner.SYNTAX_TESTS,
            "syntaxes/Example.sublime-syntax": runner.SYNTAX_COMPATIBILITY_CHECKS,
        }

        for test_file, category in cases.items():
            with self.subTest(test_file=test_file):
                self.assertEqual(
                    runner.resolve_test_categories(args, test_file),
                    (category,),
                )

    def test_rejects_unsupported_file_type(self):
        args = runner.parse_args([])

        with self.assertRaisesRegex(SystemExit, "unsupported test file type"):
            runner.resolve_test_categories(args, "tests/example.txt")


class DockerCommandTests(unittest.TestCase):
    def test_passes_selected_categories_to_container_runner(self):
        command = runner.build_docker_run_command(
            package_root=Path("/package"),
            unit_testing_root=Path("/unittesting"),
            package_name="Example",
            image="image",
            cache_volume=None,
            container_name=None,
            ignore_manifest=runner.GitIgnoreManifest(),
            test_categories=(runner.UNIT_TESTS, runner.SYNTAX_TESTS),
            scheduler_delay_ms=0,
            coverage=False,
            failfast=False,
            reload_package_on_testing=False,
            dry_run=False,
            color="never",
            tests_dir=None,
            pattern=None,
        )

        image_index = command.index("image")
        self.assertEqual(
            command[image_index + 1 : image_index + 5],
            ["run_test_categories", "--unit-tests", "--syntax-tests", "--"],
        )


if __name__ == "__main__":
    unittest.main()
