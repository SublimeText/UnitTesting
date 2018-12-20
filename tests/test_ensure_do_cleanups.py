from unittesting import DeferrableTestCase


class TestExplicitDoCleanups(DeferrableTestCase):

    def test_manually_calling_do_cleanups_works(self):
        messages = []

        def work(message):
            messages.append(message)

        self.addCleanup(work, 1)
        yield from self.doCleanups()

        self.assertEqual(messages, [1])


cleanup_called = []


class TestImplicitDoCleanupsOnTeardown(DeferrableTestCase):
    def test_a_prepare(self):
        self.addCleanup(lambda: cleanup_called.append(1))

    def test_b_assert(self):
        self.assertEqual(cleanup_called, [1])
