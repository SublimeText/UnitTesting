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
            sublime.set_timeout(check_packages, 2000)
        else:
            sublime.set_timeout(check_package_control, 2000)

    num_retries = 0

    def retry(callback):
        """
        Schedule another check, return False if out of retries.
        """
        nonlocal num_retries

        if num_retries < 20:
            num_retries += 1
            sublime.set_timeout(callback, 2000)
            return True

        return False

    def check_packages():
        """
        Wait for Package Control to install missing packages.

        PC4 automatically installs packages listed in `installed_packages`
        at startup, before installing missing libraries.
        """
        package_control = sys.modules["Package Control"].package_control
        manager = package_control.package_manager.PackageManager()
        settings = sublime.load_settings("Package Control.sublime-settings")
        missing_packages = set(settings.get("installed_packages", [])) - manager.list_packages()
        # Takes the lock that PC holds while re-enabling packages, so that
        # `ignored_packages` is saved too once a package is no longer listed.
        missing_packages |= package_control.package_disabler.PackageDisabler.in_process_packages()
        if not missing_packages:
            check_libraries()
            return

        if retry(check_packages):
            return

        log.write("missing packages:" + "\n")
        log.write("\n".join("- " + name for name in sorted(missing_packages)) + "\n")
        touch("failed")
        kill_subl(restart=False)

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
            if retry(check_libraries):
                return

            log.write("missing libraries:" + "\n")
            log.write(
                "\n".join(
                    "- {lib.name} for Python {lib.python_version}".format(lib=lib)
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
