from functools import partial
import time

import sublime

from unittesting import DeferrableTestCase


def run_in_worker(fn, *args, **kwargs):
    sublime.set_timeout_async(partial(fn, *args, **kwargs))


class TestTimingInDeferredTestCase(DeferrableTestCase):

    def test_a(self):
        messages = []

        def work(message, worktime=None):
            messages.append(message)
            # simulate that a task might take some time
            # this will not yield back but block
            if worktime:
                time.sleep(worktime)

        def uut():
            run_in_worker(work, 1, 0.5)   # add task (A)
            run_in_worker(work, 2)        # add task (B)


        uut()   # after that task queue has: (A)..(B)
        yield   # add task (C) and wait for (C)
        expected = [1, 2]
        self.assertEqual(messages, expected)

    def test_b(self):
        messages = []

        def work(message, worktime=None):
            messages.append(message)
            if worktime:
                time.sleep(worktime)

        def sub_task():
            run_in_worker(work, 2, 0.5)  # add task (D)

        def uut():
            run_in_worker(work, 1, 0.5)  # add task (A)
            run_in_worker(sub_task)      # add task (B)

        uut()
        # task queue now: (A)..(B)

        yield  # add task (C) and wait for (C)
               # (A) runs, (B) runs and adds task (D), (C) resolves
        expected = [1]
        self.assertEqual(messages, expected)
        # task queue now: (D)
        yield  # add task (E) and wait for it
               # (D) runs and (E) resolves
        expected = [1, 2]
        self.assertEqual(messages, expected)
