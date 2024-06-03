from unittesting import DeferrableViewTestCase
from unittesting import expectedFailure


class TestDeferrable(DeferrableViewTestCase):

    def test_defer(self):
        self.setText("foo")
        self.setCaretTo(0, 0)
        self.defer(100, self.insertText, "foo")
        yield 200
        self.assertRowContentsEqual(0, "foofoo")

    def test_assertion(self):
        x = []

        def append():
            x.append(1)

        self.defer(100, append)

        # check if assertion is met within timeout
        yield lambda: self.assertEqual(len(x), 1)

        self.assertEqual(x[0], 1)

    def test_condition(self):
        x = []

        def append():
            x.append(1)

        def condition():
            return len(x) == 1

        self.defer(100, append)

        # wait until `condition()` is true
        yield condition

        self.assertEqual(x[0], 1)

    @expectedFailure
    def test_condition_timeout(self):
        x = []

        def append():
            x.append(1)

        self.defer(100, append)

        # wait until condition timeout
        yield {"condition": lambda: False, "timeout": 500}

        self.assertEqual(x[0], 1)
