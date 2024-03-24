import os

from unittesting import TempDirectoryTestCase


def tidy_path(path):
    return os.path.realpath(os.path.normcase(path))


class TestTempDirectoryTestCase(TempDirectoryTestCase):

    def test_temp_dir(self):
        self.assertTrue(
            tidy_path(self._temp_dir),
            tidy_path(self.window.folders()[0])
        )
