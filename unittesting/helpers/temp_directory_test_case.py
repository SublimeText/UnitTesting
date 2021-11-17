import sublime
import os
import shutil
import tempfile
from .. import DeferrableTestCase


class TempDirectoryTestCase(DeferrableTestCase):
    """Create a temp directory and open it."""

    _temp_dir = None
    window = None

    @classmethod
    def setWindowFolder(cls):
        project_data = cls.window.project_data() or {}
        folders = project_data.get("folders", [])
        if len(folders) == 1 and folders[0]["path"] == cls._temp_dir:
            return

        project_data = {"folders": [{"path": cls._temp_dir}]}
        cls.window.set_project_data(project_data)

        def condition():
            for d in cls.window.folders():
                # on Windows, `cls._temp_dir` is lowered cased,
                # `os.path.normcase` is needed for comparison.
                if cls._temp_dir.lower() == os.path.normcase(d).lower():
                    return True

        yield condition

    @classmethod
    def setUpClass(cls):
        """
            Create a temp directory for testing.
            Note that it is a generator, if you need to extend this method, you will
            need to call

                yield from super().setUpClass()

            from the subclass. Note that if the subclass has multiple parents,
            `super().setUpClass` may not be a generator at all depends on the order.
        """
        cls._temp_dir = tempfile.mkdtemp()
        nwindows = len(sublime.windows())
        original_window_id = sublime.active_window().id()
        sublime.run_command("new_window")

        yield lambda: len(sublime.windows()) > nwindows

        yield lambda: sublime.active_window().id() != original_window_id

        cls.window = sublime.active_window()

        yield from cls.setWindowFolder()

        x = super().setUpClass()
        if hasattr(x, '__iter__'):
            yield from x

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

        x = super().tearDownClass()
        if hasattr(x, '__iter__'):
            yield from x
