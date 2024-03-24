import sys

from unittest import skipIf
from unittesting import DeferrableTestCase
from unittesting import expectedFailure

PY33 = sys.version_info == (3,3)
if PY33:
    from unittest.case import _ExpectedFailure, _UnexpectedSuccess


class TestExpectedFailures(DeferrableTestCase):
    @skipIf(not PY33, "Sublime Text 4 has optimization on")
    @expectedFailure
    def test_direct_failure1(self):
        assert False

    @expectedFailure
    def test_direct_failure2(self):
        self.assertTrue(False)

    def test_expected_failure_coroutine(self):
        @expectedFailure
        def testitem():
            yield
            1 / 0

        ex = _ExpectedFailure if PY33 else ZeroDivisionError
        try:
            yield from testitem()
        except ex:
            pass
        else:
            self.fail('Expected _ExpectedFailure')

    def test_expected_failure(self):
        @expectedFailure
        def testitem():
            1 / 0

        ex = _ExpectedFailure if PY33 else ZeroDivisionError
        try:
            yield from testitem()
        except ex:
            pass
        else:
            self.fail('Expected _ExpectedFailure')

    @skipIf(not PY33, "not applicable in Python 3.8")
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

    @skipIf(not PY33, "not applicable in Python 3.8")
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
