import sublime
import os
import shutil
import tempfile
from .. import DeferrableTestCase


class TempDirectoryTestCase(DeferrableTestCase):
    """Create a temp directory and open it."""

    _temp_dir = None

    @classmethod
    def setUpClass(cls):
        """Create a temp directory for testing."""
        cls._temp_dir = tempfile.mkdtemp()
        nwindows = len(sublime.windows())
        original_window_id = sublime.active_window().id()
        sublime.run_command("new_window")

        yield lambda: len(sublime.windows()) > nwindows

        yield lambda: sublime.active_window().id() != original_window_id

        cls.window = sublime.active_window()

        project_data = dict(folders=[dict(follow_symlinks=True, path=cls._temp_dir)])
        cls.window.set_project_data(project_data)

        def condition():
            for d in cls.window.folders():
                # on Windows, `cls._temp_dir` is lowered cased,
                # `os.path.normcase` is needed for comparison.
                if cls._temp_dir == os.path.normcase(d):
                    return True

        yield condition

    @classmethod
    def tearDownClass(cls):
        # need at least one window in order to keep sublime running
        if len(sublime.windows()) > 1:
            cls.window.run_command('close_window')

            def remove_temp_dir():
                try:
                    shutil.rmtree(cls._temp_dir)
                except Exception:
                    print("Cannot remove {}".format(cls._temp_dir))

            sublime.set_timeout(remove_temp_dir, 1000)
