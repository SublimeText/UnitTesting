import os
import sublime
import subprocess
import sys


def plugin_loaded():
    package_path = os.path.join(
        sublime.packages_path(), "0_install_package_control_helper"
    )

    logfile = os.path.join(package_path, "log")

    log = open(logfile, "a", encoding="utf-8")

    sys.stdout = log
    sys.stderr = log

    def kill_subl(restart=False):
        log.close()

        if sublime.platform() == "osx":
            cmd = "pkill subl"
            if restart:
                cmd += "; sleep 1; subl'"
        elif sublime.platform() == "linux":
            cmd = "pkill subl"
            if restart:
                cmd += "; sleep 1; subl"
        elif sublime.platform() == "windows":
            cmd = "taskkill /F /im sublime_text.exe"
            if restart:
                cmd += ' & sleep 1 & "{}"'.format(sublime.executable_path())
        else:
            return

        subprocess.Popen(cmd, shell=True)

    def touch(file_name):
        open(os.path.join(package_path, file_name), "a").close()

    def check_package_control():
        """
        Wait for Package Control to be loaded.
        """
        if "Package Control" in sys.modules:
            sublime.set_timeout(check_libraries, 2000)
        else:
            sublime.set_timeout(check_package_control, 2000)

    num_retries = 0

    def check_libraries():
        """
        Wait for Package Control to finish bootstrapping.

        PC4 automatically installs missing libraries at startup
        just need to wait for it being completed.
        """
        package_control = sys.modules["Package Control"].package_control
        manager = package_control.package_manager.PackageManager()
        missing_libraries = manager.find_missing_libraries()
        if missing_libraries:
            nonlocal num_retries

            if num_retries < 10:
                num_retries += 1
                sublime.set_timeout(check_libraries, 2000)
                return

            log.write("missing libraries:" + "\n")
            log.write(
                "\n".join(
                    "- {lib.name} for Python {lib.python_version}".format(lib)
                    for lib in sorted(missing_libraries)
                )
                + "\n"
            )
            touch("failed")
        else:
            touch("success")

        kill_subl(restart=False)

    def error_message(message):
        """Restart sublime when `sublime.error_message()` is run."""
        log.write(message + "\n")
        kill_subl(restart=True)

    def info_message(message):
        """Print output from `sublime.message_dialog()` to logfile."""
        log.write(message + "\n")

    sublime.error_message = error_message
    sublime.message_dialog = info_message
    sublime.set_timeout(check_package_control, 2000)
