import sublime
import time

from functools import partial
from unittesting import AWAIT_WORKER
from unittesting import DeferrableTestCase


def run_in_worker(fn, *args, **kwargs):
    sublime.set_timeout_async(partial(fn, *args, **kwargs))


class TestAwaitingWorkerInDeferredTestCase(DeferrableTestCase):

    def test_ensure_plain_yield_is_faster_than_the_worker_thread(self):
        messages = []

        def work(message, worktime=None):
            # simulate that a task might take some time
            # this will not yield back but block
            if worktime:
                time.sleep(worktime)

            messages.append(message)

        run_in_worker(work, 1, 5)

        yield

        self.assertEqual(messages, [])

    def test_await_worker(self):
        messages = []

        def work(message, worktime=None):
            # simulate that a task might take some time
            # this will not yield back but block
            if worktime:
                time.sleep(worktime)

            messages.append(message)

        run_in_worker(work, 1, 0.5)

        yield AWAIT_WORKER

        self.assertEqual(messages, [1])
