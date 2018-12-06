from unittesting import DeferrableTestCase


class TestDoCleanups(DeferrableTestCase):

    def test_ensure_do_cleanups_works(self):
        messages = []

        def work(message):
            messages.append(message)

        self.addCleanup(work, 1)
        yield from self.doCleanups()

        self.assertEqual(messages, [1])
