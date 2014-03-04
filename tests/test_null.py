import sublime
from unittest import TestCase

version = sublime.version()

class TestNULL(TestCase):

    def test_null(self):
        self.assertEqual(1,1)