"""Runs a test suite against Sublime Text.

Usage:

1. cd path/to/PACKAGE
2. python path/to/run_tests.py PACKAGE
"""

from __future__ import print_function
import json
import optparse
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile

# todo: allow different sublime versions

PACKAGES_DIR_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))
UT_OUTPUT_DIR_PATH = os.path.realpath(os.path.join(PACKAGES_DIR_PATH, 'User', 'UnitTesting'))
SCHEDULE_FILE_PATH = os.path.realpath(os.path.join(UT_OUTPUT_DIR_PATH, 'schedule.json'))
UT_DIR_PATH = os.path.realpath(os.path.join(PACKAGES_DIR_PATH, 'UnitTesting'))
UT_SBIN_PATH = os.path.realpath(os.path.join(PACKAGES_DIR_PATH, 'UnitTesting', 'sbin'))
SCHEDULE_RUNNER_SOURCE = os.path.join(UT_SBIN_PATH, "run_scheduler.py")
SCHEDULE_RUNNER_TARGET = os.path.join(UT_DIR_PATH, "zzz_run_scheduler.py")
DONE_MESSAGE = "UnitTesting: Done.\n"
RX_RESULT = re.compile(r'^(?P<result>OK|FAILED|ERROR)', re.MULTILINE)
RX_DONE = re.compile(r'^UnitTesting: Done\.$', re.MULTILINE)
RX_TEST_STATUS = re.compile(r'\.\.\. (ok|FAIL|ERROR|skipped)(\b.*)$')
RX_SUMMARY_OK = re.compile(r'^OK(?:\b.*)?$')
RX_SUMMARY_FAIL = re.compile(r'^(FAILED|ERROR)(?:\b.*)?$')

ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_CYAN = "\033[36m"

_is_windows = sys.platform == 'win32'


def create_dir_if_not_exists(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def delete_file_if_exists(path):
    if os.path.exists(path):
        os.unlink(path)


def copy_file_if_not_exists(source, target):
    if not os.path.exists(target):
        shutil.copyfile(source, target)


def create_schedules(package, named_schedules):
    schedule = []

    try:
        with open(SCHEDULE_FILE_PATH, 'r') as f:
            schedule = json.load(f)
    except Exception:
        pass

    schedule = [item for item in schedule if item.get('package') != package]
    schedule.extend(default_schedule for _, default_schedule in named_schedules)

    with open(SCHEDULE_FILE_PATH, 'w') as f:
        f.write(json.dumps(schedule, ensure_ascii=False, indent=True))


def wait_for_output(path, schedule, timeout=10, poll_interval=0.2):
    start_time = time.time()
    last_dot = 0

    def check_has_timed_out():
        return time.time() - start_time > timeout

    def check_is_output_available():
        try:
            return os.stat(path).st_size != 0
        except Exception:
            pass

    while not check_is_output_available():
        now = time.time()
        if now - last_dot >= 1:
            print(".", end="")
            sys.stdout.flush()
            last_dot = now

        if check_has_timed_out():
            print()
            delete_file_if_exists(schedule)
            raise ValueError('timeout')

        time.sleep(poll_interval)
    else:
        print()


def start_sublime_text():
    subprocess.Popen("subl --stay &", shell=True)


def kill_sublime_text():
    subprocess.Popen("pkill [Ss]ubl || true", shell=True)
    subprocess.Popen("pkill plugin_host || true", shell=True)


def read_output(path, color='auto', show_done=True):
    # todo: use notification instead of polling
    success = None
    use_color = should_use_color(color)
    pending = ""

    def check_is_success(result):
        try:
            return RX_RESULT.search(result).group('result') == 'OK'
        except AttributeError:
            return success

    def check_is_done(result):
        return RX_DONE.search(result) is not None

    with open(path, 'r') as f:
        while True:
            offset = f.tell()
            result = f.read()

            if result:
                display_result = result if show_done else result.replace(DONE_MESSAGE, "")
                if use_color:
                    rendered, pending = colorize_output_chunk(display_result, pending)
                    print(rendered, end="")
                else:
                    print(display_result, end="")
                sys.stdout.flush()

            # Keep checking while we don't have a definite result.
            success = check_is_success(result)

            if check_is_done(result):
                assert success is not None, 'final test result must not be None'
                break
            elif not result:
                f.seek(offset)

            time.sleep(0.2)

    if use_color and pending:
        print(colorize_output_line(pending), end="")
        sys.stdout.flush()

    return success


def should_use_color(mode):
    if mode == 'always':
        return True

    if mode == 'never':
        return False

    if os.environ.get('NO_COLOR') is not None:
        return False

    if os.environ.get('CLICOLOR_FORCE') not in (None, '', '0'):
        return True

    if os.environ.get('FORCE_COLOR') not in (None, '', '0'):
        return True

    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def colorize_output_chunk(chunk, pending):
    if not chunk:
        return '', pending

    text = pending + chunk
    lines = text.splitlines(True)

    if lines and not lines[-1].endswith(('\n', '\r')):
        pending = lines.pop()
    else:
        pending = ''

    rendered = ''.join(colorize_output_line(line) for line in lines)
    return rendered, pending


def colorize_output_line(line):
    newline = ''
    body = line

    if body.endswith('\r\n'):
        body = body[:-2]
        newline = '\r\n'
    elif body.endswith('\n') or body.endswith('\r'):
        body = body[:-1]
        newline = line[-1]

    test_status_match = RX_TEST_STATUS.search(body)
    if test_status_match:
        status = test_status_match.group(1)
        suffix = test_status_match.group(2)
        body = (
            body[:test_status_match.start()]
            + '... '
            + colorize_status(status)
            + suffix
        )

    if RX_SUMMARY_OK.match(body):
        body = ANSI_GREEN + body + ANSI_RESET
    elif RX_SUMMARY_FAIL.match(body):
        body = ANSI_RED + body + ANSI_RESET
    elif body.startswith('Ran '):
        body = ANSI_CYAN + body + ANSI_RESET

    return body + newline


def colorize_status(status):
    if status == 'ok':
        return ANSI_GREEN + status + ANSI_RESET

    if status == 'skipped':
        return ANSI_YELLOW + status + ANSI_RESET

    return ANSI_RED + status + ANSI_RESET


def restore_coverage_file(path, package):
    # restore .coverage if it exists, needed for coveralls
    if os.path.exists(path):
        with open(path, 'r') as f:
            txt = f.read()
        txt = txt.replace(os.path.realpath(os.path.join(PACKAGES_DIR_PATH, package)), os.getcwd())
        with open(os.path.join(os.getcwd(), ".coverage"), "w") as f:
            f.write(txt)


def print_runtime_metadata():
    sublime_text_version = detect_sublime_text_version()
    package_control_version = detect_package_control_version()

    print("Runtime:")
    print("  Sublime Text: {}".format(sublime_text_version or "unknown"))
    print("  Package Control: {}".format(package_control_version or "unknown"))


def detect_sublime_text_version():
    try:
        output = subprocess.check_output(
            ["subl", "--version"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
    except Exception:
        return None

    for line in output.splitlines():
        line = line.strip()
        if line:
            return line

    return None


def detect_package_control_version():
    installed_packages_dir = os.path.join(
        os.path.dirname(PACKAGES_DIR_PATH),
        "Installed Packages",
    )
    package_path = os.path.join(
        installed_packages_dir,
        "Package Control.sublime-package",
    )
    if not os.path.isfile(package_path):
        return None

    try:
        with zipfile.ZipFile(package_path, "r") as package_zip:
            metadata = json.loads(package_zip.read("package-metadata.json").decode("utf-8"))
    except Exception:
        return None

    version = metadata.get("version") if isinstance(metadata, dict) else None
    return str(version) if version else None


def main(named_schedules, dry_run=False, color='auto'):
    package_under_test = named_schedules[0][1]['package']
    output_dir = os.path.join(UT_OUTPUT_DIR_PATH, package_under_test)
    coverage_file = os.path.join(output_dir, "coverage")
    output_files = configure_schedule_outputs(named_schedules, output_dir)

    print_runtime_metadata()
    print_schedules(named_schedules)

    if dry_run:
        create_dir_if_not_exists(output_dir)
        delete_files(output_files)
        delete_file_if_exists(coverage_file)
        create_schedules(package_under_test, named_schedules)
        return

    for i in range(3):
        create_dir_if_not_exists(output_dir)
        delete_files(output_files)
        delete_file_if_exists(coverage_file)
        create_schedules(package_under_test, named_schedules)
        delete_file_if_exists(SCHEDULE_RUNNER_TARGET)
        copy_file_if_not_exists(SCHEDULE_RUNNER_SOURCE, SCHEDULE_RUNNER_TARGET)
        start_sublime_text()
        try:
            for name, output_file in output_files:
                print("Wait for %s output..." % name, end="")
                wait_for_output(output_file, SCHEDULE_RUNNER_TARGET)
            break
        except ValueError:
            if i == 2:
                print("Timeout: Could not obtain tests output.")
                print("Maybe Sublime Text is not responding or the tests output "
                      "is being written to the wrong file.")
                delete_file_if_exists(SCHEDULE_RUNNER_TARGET)
                sys.exit(1)
            print("Retrying after Sublime Text did not produce test output.")
            kill_sublime_text()
            time.sleep(2)

    success = True
    show_category_done = len(output_files) == 1
    for name, output_file in output_files:
        print("=== %s OUTPUT ===" % name.upper())
        if not read_output(output_file, color=color, show_done=show_category_done):
            success = False

    if not show_category_done:
        print(DONE_MESSAGE, end="")

    if not success:
        sys.exit(1)
    restore_coverage_file(coverage_file, package_under_test)
    delete_file_if_exists(SCHEDULE_RUNNER_TARGET)


def print_schedules(named_schedules):
    for name, schedule in named_schedules:
        heading = 'Schedule:' if len(named_schedules) == 1 else 'Schedule (%s):' % name
        print(heading)
        for key, value in schedule.items():
            print('  %s: %s' % (key, value))


def configure_schedule_outputs(named_schedules, output_dir):
    output_files = []
    for name, schedule in named_schedules:
        output_name = (
            "result"
            if len(named_schedules) == 1
            else "result-" + name.replace(" ", "-")
        )
        output_file = os.path.join(output_dir, output_name)
        schedule['output'] = output_file
        output_files.append((name, output_file))
    return output_files


def delete_files(named_files):
    for _, path in named_files:
        delete_file_if_exists(path)


def build_named_schedules(options, package):
    schedule_options = {
        'package': package,
        'coverage': options.coverage,
        'reload_package_on_testing': bool(options.reload_package_on_testing),
    }

    if options.pattern:
        schedule_options['pattern'] = options.pattern
    if options.tests_dir:
        schedule_options['tests_dir'] = options.tests_dir
    if not options.fail_if_no_resources:
        schedule_options['fail_if_no_resources'] = False
    if options.failfast:
        schedule_options['failfast'] = True

    named_schedules = []
    explicit_category = any(
        (
            options.unit_test,
            options.syntax_test,
            options.syntax_compatibility,
            options.color_scheme_test,
        )
    )
    if options.syntax_test:
        named_schedules.append(
            ('syntax tests', dict(schedule_options, syntax_test=True))
        )
    if options.syntax_compatibility:
        named_schedules.append(
            (
                'syntax compatibility checks',
                dict(schedule_options, syntax_compatibility=True),
            )
        )
    if options.color_scheme_test:
        named_schedules.append(
            ('color scheme tests', dict(schedule_options, color_scheme_test=True))
        )

    # Unit tests may continue through deferred callbacks after their command
    # returns, so keep them last to avoid overlapping another category.
    if options.unit_test or not explicit_category:
        named_schedules.append(('unit tests', schedule_options))

    return named_schedules


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--unit-test', action='store_true')
    parser.add_option('--syntax-test', action='store_true')
    parser.add_option('--syntax-compatibility', action='store_true')
    parser.add_option('--color-scheme-test', action='store_true')
    parser.add_option('--coverage', action='store_true')
    parser.add_option('--pattern')
    parser.add_option('--tests-dir')
    parser.add_option(
        '--no-fail-if-no-resources',
        action='store_false',
        dest='fail_if_no_resources',
        default=True,
    )
    parser.add_option('--failfast', action='store_true')
    parser.add_option('--reload-package-on-testing', action='store_true')
    parser.add_option('--dry-run', action='store_true')
    parser.add_option(
        '--color',
        type='choice',
        choices=['auto', 'always', 'never'],
        default='auto',
        help='Colorize test output (auto, always, never).',
    )

    options, remainder = parser.parse_args()

    package_under_test = remainder[0] if len(remainder) > 0 else "UnitTesting"
    named_schedules = build_named_schedules(options, package_under_test)
    main(named_schedules, dry_run=options.dry_run, color=options.color)
