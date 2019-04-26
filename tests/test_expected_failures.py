from unittest.case import _ExpectedFailure, _UnexpectedSuccess
from unittesting import DeferrableTestCase, expectedFailure


class TestExpectedFailures(DeferrableTestCase):
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
