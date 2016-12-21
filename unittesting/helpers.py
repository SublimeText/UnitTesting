import sublime
import subprocess
import os
import shutil
import tempfile
from . import DeferrableTestCase


def subl(*args):
    executable_path = sublime.executable_path()
    if sublime.platform() == 'osx':
        app_path = executable_path[:executable_path.rfind(".app/") + 5]
        executable_path = app_path + "Contents/SharedSupport/bin/subl"
    subprocess.Popen([executable_path] + list(args))
    if sublime.platform() == "windows":
        def fix_focus():
            window = sublime.active_window()
            view = window.active_view()
            window.run_command('focus_neighboring_group')
            window.focus_view(view)
        sublime.set_timeout(fix_focus, 300)


class TempDirectoryTestCase(DeferrableTestCase):
    """
    Create a temp directory and open it.
    """

    _temp_dir = None

    @classmethod
    def setUpClass(cls):
        """
        Setup a temp directory for testing
        """
        cls._temp_dir = tempfile.mkdtemp()
        subl("-n", cls._temp_dir)

        def condition():
            for d in sublime.active_window().folders():
                # on Windows, `cls._temp_dir` is lowered cased,
                # `os.path.normcase` is needed for comparison.
                if cls._temp_dir == os.path.normcase(d):
                    return True

        yield condition

        cls.window = sublime.active_window()

    @classmethod
    def tearDownClass(cls):
        # need at least one window in order to keep sublime running
        if len(sublime.windows()) > 1:
            cls.window.run_command("close")

            def remove_temp_dir():
                try:
                    shutil.rmtree(cls._temp_dir)
                except:
                    print("Cannot remove {}".format(cls._temp_dir))

            sublime.set_timeout(remove_temp_dir, 1000)
