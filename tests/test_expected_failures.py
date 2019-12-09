import sublime

try:
    from unittest.case import _ExpectedFailure, _UnexpectedSuccess
except ImportError:
    pass
from unittest import skipIf
from unittesting import DeferrableTestCase, expectedFailure


class TestExpectedFailures(DeferrableTestCase):
    @skipIf(sublime.version() >= '4000', "Sublime Text 4 has optimization on")
    @expectedFailure
    def test_direct_failure1(self):
        assert False

    @expectedFailure
    def test_direct_failure2(self):
        self.assertTrue(False)

    @skipIf(sublime.version() >= '4000', "not applicable in Python 3.8")
    def test_expected_failure_coroutine(self):
        @expectedFailure
        def testitem():
            yield
            1 / 0

        try:
            yield from testitem()
        except _ExpectedFailure:
            pass
        else:
            self.fail('Expected _ExpectedFailure')

    @skipIf(sublime.version() >= '4000', "not applicable in Python 3.8")
    def test_expected_failure(self):
        @expectedFailure
        def testitem():
            1 / 0

        try:
            yield from testitem()
        except _ExpectedFailure:
            pass
        else:
            self.fail('Expected _ExpectedFailure')

    @skipIf(sublime.version() >= '4000', "not applicable in Python 3.8")
    def test_unexpected_success_coroutine(self):

        @expectedFailure
        def testitem():
            yield

        try:
            yield from testitem()
        except _UnexpectedSuccess:
            pass
        else:
            self.fail('Expected _UnexpectedSuccess')

    @skipIf(sublime.version() >= '4000', "not applicable in Python 3.8")
    def test_unexpected_success(self):

        @expectedFailure
        def testitem():
            ...

        try:
            yield from testitem()
        except _UnexpectedSuccess:
            pass
        else:
            self.fail('Expected _UnexpectedSuccess')
