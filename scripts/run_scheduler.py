"""
Schedule runner plugin.

This module ...
1. is copied to $st_data/Packages/UnitTesting/run_scheduler.py
2. loaded as Sublime Text plugin
3. invokes scheduled package tests
"""
import sublime

from .unittesting import run_scheduler


def error_message(message):
    print(message)


# redirect ST error and message boxes to console only
sublime.error_message = error_message
sublime.message_dialog = error_message


def plugin_loaded():
    run_scheduler()
