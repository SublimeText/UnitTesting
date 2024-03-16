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
import threading

# todo: allow different sublime versions

PACKAGES_DIR_PATH = os.environ.get("SUBLIME_TEXT_PACKAGES", os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..')))
UT_OUTPUT_DIR_PATH = os.path.realpath(os.path.join(PACKAGES_DIR_PATH, 'User', 'UnitTesting'))
SCHEDULE_FILE_PATH = os.path.realpath(os.path.join(UT_OUTPUT_DIR_PATH, 'schedule.json'))
UT_DIR_PATH = os.path.realpath(os.path.join(PACKAGES_DIR_PATH, 'UnitTesting'))
SCHEDULE_RUNNER_SOURCE = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__))), "run_scheduler.py")
SCHEDULE_RUNNER_TARGET = os.path.join(UT_DIR_PATH, "zzz_run_scheduler.py")
RX_RESULT = re.compile(r'^(?P<result>OK|FAILED|ERROR)', re.MULTILINE)
RX_DONE = re.compile(r'^UnitTesting: Done\.$', re.MULTILINE)

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


def create_schedule(package, output_file, default_schedule):
    schedule = []

    try:
        with open(SCHEDULE_FILE_PATH, 'r') as f:
            schedule = json.load(f)
    except Exception:
        pass

    if not any(s['package'] == package for s in schedule):
        schedule.append(default_schedule)

    with open(SCHEDULE_FILE_PATH, 'w') as f:
        f.write(json.dumps(schedule, ensure_ascii=False, indent=True))


def wait_for_output(path, schedule, timeout=30):
    start_time = time.time()
    needs_newline = False

    def check_has_timed_out():
        return time.time() - start_time > timeout

    def check_is_output_available():
        try:
            return os.stat(path).st_size != 0
        except Exception:
            pass

    while not check_is_output_available():
        print(".", end="")
        sys.stdout.flush()
        needs_newline = True

        if check_has_timed_out():
            print()
            delete_file_if_exists(schedule)
            raise ValueError('timeout')

        time.sleep(1)
    else:
        if needs_newline:
            print()


def start_sublime_text():
    if _is_windows:
        subprocess.Popen("sublime_text.exe")
    else:
        subprocess.Popen("subl --stay &", shell=True)


def kill_sublime_text():
    if _is_windows:
        subprocess.Popen([
            "pwsh",
            "-command",
            "stop-process -force -processname sublime_text -ea silentlycontinue"])
    else:
        subprocess.Popen("pkill [Ss]ubl || true", shell=True)
        subprocess.Popen("pkill plugin_host || true", shell=True)


def read_output(path, timeout=5 * 60):
    # todo: use notification instead of polling
    success = None
    done = False
    lines = []
    linebuffer = [""]

    def check_is_success(result):
        try:
            return RX_RESULT.search(result).group('result') == 'OK'
        except AttributeError:
            return success

    lock = threading.Lock()

    def reader():
        with open(path, 'r') as f:
            while not done:
                offset = f.tell()
                line = f.readline()
                if line.endswith("\n"):
                    with lock:
                        lines.append(line)
                else:
                    with lock:
                        linebuffer[0] = line
                    f.seek(offset)
                    time.sleep(0.2)

    # run the reader in thread to avoid blocking
    t = threading.Thread(target=reader)
    t.start()
    last_update_time = time.time()

    while not done:
        if time.time() - last_update_time > timeout:
            with lock:
                print(linebuffer[0])
            done = True
            raise TimeoutError()

        # consume one line
        with lock:
            if lines:
                last_update_time = time.time()
                line = lines.pop(0)
            else:
                line = None

        if line is None:
            time.sleep(0.2)
            continue

        print(line, end="")
        # Keep checking while we don't have a definite result.
        success = check_is_success(line)

        if RX_DONE.search(line) is not None:
            done = True
            assert success is not None, 'Cannot determine test results.'
            break

    return success


def restore_coverage_report(report_file):
    # restore coverage.xml if it exists, needed for coveralls
    if os.path.isfile(report_file):
        source_path, name = os.path.splitext(report_file)
        dest_path = os.getcwd()
        with open(report_file, 'r') as f:
            txt = f.read()
        txt = txt.replace(source_path, dest_path)
        with open(os.path.join(dest_path, name), "w") as f:
            f.write(txt)


def main(default_schedule_info):
    package_under_test = default_schedule_info['package']
    output_dir = os.path.join(UT_OUTPUT_DIR_PATH, package_under_test)
    output_file = os.path.join(output_dir, "result")
    coverage_file = os.path.join(output_dir, "coverage")
    report_file = os.path.join(PACKAGES_DIR_PATH, package_under_test, "coverage.xml")

    default_schedule_info['output'] = output_file

    for i in range(3):
        create_dir_if_not_exists(output_dir)
        delete_file_if_exists(output_file)
        delete_file_if_exists(coverage_file)
        delete_file_if_exists(report_file)
        create_schedule(package_under_test, output_file, default_schedule_info)
        delete_file_if_exists(SCHEDULE_RUNNER_TARGET)
        copy_file_if_not_exists(SCHEDULE_RUNNER_SOURCE, SCHEDULE_RUNNER_TARGET)
        start_sublime_text()
        try:
            print("Wait for tests output...", end="")
            wait_for_output(output_file, SCHEDULE_RUNNER_TARGET)
            break
        except ValueError:
            if i == 2:
                print("Timeout: Could not obtain tests output.")
                print("Maybe Sublime Text is not responding or the tests output "
                      "is being written to the wrong file.")
                delete_file_if_exists(SCHEDULE_RUNNER_TARGET)
                sys.exit(1)
            kill_sublime_text()
            time.sleep(2)

    print("Start to read output...")
    try:
        if not read_output(output_file):
            sys.exit(1)
    except TimeoutError:
        print("Timeout: output is frozen.")
        delete_file_if_exists(SCHEDULE_RUNNER_TARGET)
        sys.exit(1)
    restore_coverage_report(report_file)
    delete_file_if_exists(SCHEDULE_RUNNER_TARGET)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--syntax-test', action='store_true')
    parser.add_option('--syntax-compatibility', action='store_true')
    parser.add_option('--color-scheme-test', action='store_true')
    parser.add_option('--coverage', action='store_true')

    options, remainder = parser.parse_args()

    syntax_test = options.syntax_test
    syntax_compatibility = options.syntax_compatibility
    color_scheme_test = options.color_scheme_test
    coverage = options.coverage
    package_under_test = remainder[0] if len(remainder) > 0 else "UnitTesting"

    default_schedule_info = {
        'package': package_under_test,
        'syntax_test': syntax_test,
        'syntax_compatibility': syntax_compatibility,
        'color_scheme_test': color_scheme_test,
        'coverage': coverage,
    }

    main(default_schedule_info)
