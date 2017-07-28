import sublime
import sys
import subprocess
import os


def plugin_loaded():

    pc_settings = sublime.load_settings("Package Control.sublime-settings")

    def kill_subl(restart=False):
        if sublime.platform() == "osx":
            cmd = "sleep 1; killall 'Sublime Text'; sleep 1; "
            if restart:
                cmd = cmd + "osascript -e 'tell application \"Sublime Text\" to activate'"
        elif sublime.platform() == "linux":
            cmd = "sleep 1; killall 'subl'; sleep 1; "
            if restart:
                cmd = cmd + "subl"
        elif sublime.platform() == "windows":
            cmd = "sleep 1 & taskkill /F /im sublime_text.exe & sleep 1 "
            if restart:
                cmd = cmd + "& \"C:\\st\\sublime_text.exe\""

        subprocess.Popen(cmd, shell=True)

    def touch(file_name):
        f = os.path.join(
            sublime.packages_path(),
            "0_install_package_control_helper",
            file_name)
        open(f, 'a').close()

    def check_bootstrap():
        if pc_settings.get("bootstrapped", False):
            touch("bootstrapped")
            kill_subl(True)
        else:
            sublime.set_timeout(check_bootstrap, 20)

    def check_dependencies():
        if 'Package Control' in sys.modules:
            package_control = sys.modules['Package Control'].package_control
        else:
            sublime.set_timeout(check_dependencies, 20)
            return

        manager = package_control.package_manager.PackageManager()
        required_dependencies = set(manager.find_required_dependencies())

        class myPackageCleanup(package_control.package_cleanup.PackageCleanup):

            def finish(self, installed_packages, found_packages, found_dependencies):
                missing_dependencies = required_dependencies - set(found_dependencies)
                if len(missing_dependencies) == 0:
                    touch("success")
                    kill_subl()
                else:
                    sublime.set_timeout(_check_dependencies, 20)

        def _check_dependencies():
            myPackageCleanup().run()

        _check_dependencies()

    if not os.path.exists(os.path.join(
            sublime.packages_path(),
            "0_install_package_control_helper",
            "bootstrapped")):
        check_bootstrap()
    else:
        check_dependencies()

if sublime.version() < '3000':
    plugin_loaded()
