"""Runs a test suite against Sublime Text.

Usage:

1. cd path/to/PACKAGE
2. python path/to/run_tests.py PACKAGE
"""

import json
import optparse
import os
import re
import shutil
import subprocess
import sys
import asyncio
import time
from typing import Any, Dict, Optional


# todo: allow different sublime versions

PACKAGES_DIR_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))
UT_OUTPUT_DIR_PATH = os.path.realpath(os.path.join(PACKAGES_DIR_PATH, 'User', 'UnitTesting'))
SCHEDULE_FILE_PATH = os.path.realpath(os.path.join(UT_OUTPUT_DIR_PATH, 'schedule.json'))
UT_DIR_PATH = os.path.realpath(os.path.join(PACKAGES_DIR_PATH, 'UnitTesting'))
UT_SBIN_PATH = os.path.realpath(os.path.join(PACKAGES_DIR_PATH, 'UnitTesting', 'sbin'))
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


def create_schedule(package, default_schedule):
    schedule = []

    try:
        with open(SCHEDULE_FILE_PATH, 'r') as f:
            schedule = json.load(f)
    except Exception:
        pass

    if not any(s['package'] == package for s in schedule):
        print('Schedule:')
        for k, v in default_schedule.items():
            print('  %s: %s' % (k, v))

        schedule.append(default_schedule)

    with open(SCHEDULE_FILE_PATH, 'w') as f:
        f.write(json.dumps(schedule, ensure_ascii=False, indent=True))


def blocking_shell_cmd(cmd: str) -> int:
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    return p.wait()


def start_sublime_text():
    return blocking_shell_cmd("subl &")


def kill_sublime_text():
    blocking_shell_cmd("pkill [Ss]ubl || true")
    blocking_shell_cmd("pkill plugin_host || true")


def run_sublime_application_command(
    cmd: str,
    args: Optional[Dict[str, Any]] = None
) -> int:
    if args is not None:
        command = f"{cmd} '{json.dumps(args)}'"
    else:
        command = cmd
    return blocking_shell_cmd(f"subl --command {command}")


success: Optional[bool] = None


async def read_output(
    reader: asyncio.StreamReader,
    _: asyncio.StreamWriter
) -> None:
    try:
        while not reader.at_eof():
            line = str(await reader.readline(), encoding='UTF-8').rstrip()
            print(line)
            global success
            match = RX_RESULT.search(line)
            if match:
                success = match.group('result') == 'OK'
            else:
                match = RX_DONE.search(line)
                if match:
                    assert success is not None
                    asyncio.get_running_loop().stop()
    except Exception as ex:
        print("ERROR:", ex, file=sys.stderr)
        asyncio.get_running_loop().stop()


def restore_coverage_file(path, package):
    # restore .coverage if it exists, needed for coveralls
    if os.path.exists(path):
        with open(path, 'r') as f:
            txt = f.read()
        txt = txt.replace(os.path.realpath(os.path.join(PACKAGES_DIR_PATH, package)), os.getcwd())
        with open(os.path.join(os.getcwd(), ".coverage"), "w") as f:
            f.write(txt)


def main(default_schedule_info):
    package_under_test = default_schedule_info['package']
    output_dir = os.path.join(UT_OUTPUT_DIR_PATH, package_under_test)
    ping_file = os.path.join(UT_OUTPUT_DIR_PATH, "ready")
    coverage_file = os.path.join(output_dir, "coverage")
    port = 34151
    default_schedule_info['tcp_port'] = port
    create_dir_if_not_exists(output_dir)
    create_schedule(package_under_test, default_schedule_info)
    delete_file_if_exists(coverage_file)
    delete_file_if_exists(ping_file)
    start_sublime_text()
    coro = asyncio.start_server(read_output, host='localhost', port=port)
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(coro)
    while not os.path.exists(ping_file):
        time.sleep(0.1)
        run_sublime_application_command("unit_testing_ping")
    delete_file_if_exists(ping_file)
    run_sublime_application_command("unit_testing_run_scheduler")
    loop.run_forever()
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
    kill_sublime_text()
    restore_coverage_file(coverage_file, package_under_test)
    exit(0 if success else 1)


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
