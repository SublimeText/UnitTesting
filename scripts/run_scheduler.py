import os
import sublime
import sys

from .unittesting import run_scheduler

log = open(
    os.path.join(os.path.dirname(__file__), "unittesting.log"),
    "a",
    encoding="utf-8",
    buffering=1,
)

# redirect ST console output to a logfile
sys.stdout = log
sys.stderr = log


def error_message(message):
    print(message)


# redirect ST error and message boxes to console only
sublime.error_message = error_message
sublime.message_dialog = error_message


def plugin_loaded():
    run_scheduler()
