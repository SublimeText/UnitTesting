import os
import sublime
import subprocess
import sys


def plugin_loaded():
    logfile = os.path.join(
        sublime.packages_path(), "0_install_package_control_helper", "log"
    )

    log = open(logfile, "a", encoding="utf-8")

    sys.stdout = log
    sys.stderr = log

    def kill_subl(restart=False):
        log.close()

        if sublime.platform() == "osx":
            cmd = "sleep 1; pkill [Ss]ubl; pkill plugin_host; sleep 1; "
            if restart:
                cmd = (
                    cmd + "osascript -e 'tell application \"Sublime Text\" to activate'"
                )
        elif sublime.platform() == "linux":
            cmd = "sleep 1; pkill [Ss]ubl; pkill plugin_host; sleep 1; "
            if restart:
                cmd = cmd + "subl"
        elif sublime.platform() == "windows":
            cmd = "sleep 1 & taskkill /F /im sublime_text.exe & sleep 1 "
            if restart:
                cmd = cmd + '& "{}"'.format(sublime.executable_path())
        else:
            return

        subprocess.Popen(cmd, shell=True)

    def touch(file_name):
        f = os.path.join(
            sublime.packages_path(), "0_install_package_control_helper", file_name
        )
        open(f, "a").close()

    def satisfy_libraries():
        if "Package Control" in sys.modules:
            package_control = sys.modules["Package Control"].package_control
        else:
            sublime.set_timeout(satisfy_libraries, 5000)
            return

        manager = package_control.package_manager.PackageManager()

        # query and install missing libraries
        required_libraries = manager.find_required_libraries()
        if required_libraries:
            manager.install_libraries(required_libraries, fail_early=False)

        # re-query missing libraries
        missing_libraries = manager.find_missing_libraries(
            required_libraries=required_libraries
        )
        if missing_libraries:
            log.write("missing dependencies:" + "\n")
            log.write(" ".join(sorted(missing_libraries)) + "\n")
        else:
            touch("success")

        kill_subl()

    # restart sublime when `sublime.error_message` is run
    def error_message(message):
        log.write(message + "\n")
        kill_subl(True)

    sublime.error_message = error_message
    sublime.message_dialog = error_message
    sublime.set_timeout(satisfy_libraries, 5000)
