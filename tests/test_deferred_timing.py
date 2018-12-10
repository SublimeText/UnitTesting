from functools import partial
import time
from unittest.mock import patch

import sublime

from unittesting import DeferrableTestCase


def run_in_worker(fn, *args, **kwargs):
    sublime.set_timeout_async(partial(fn, *args, **kwargs))


# When we swap `set_timeout_async` with `set_timeout` we basically run
# our program single-threaded.
# This has some benefits:
# - We avoid async/timing issues
# - We can use plain `yield` to run Sublime's task queue empty, see below
# - Every code we run will get correct coverage
#
# However note, that Sublime will just put all async events on the queue,
# avoiding the API. We cannot patch that. That means, the event handlers
# will *not* run using plain `yield` like below, you still have to await
# them using `yield AWAIT_WORKER`.
#

class TestTimingInDeferredTestCase(DeferrableTestCase):

    def test_a(self):
        # `patch` doesn't work as a decorator with generator functions so we
        # use `with`
        with patch.object(sublime, 'set_timeout_async', sublime.set_timeout):
            messages = []

            def work(message, worktime=None):
                # simulate that a task might take some time
                # this will not yield back but block
                if worktime:
                    time.sleep(worktime)

                messages.append(message)

            def uut():
                run_in_worker(work, 1, 0.5)   # add task (A)
                run_in_worker(work, 2)        # add task (B)

            uut()   # after that task queue has: (A)..(B)
            yield   # add task (C) and wait for (C)
            expected = [1, 2]
            self.assertEqual(messages, expected)

    def test_b(self):
        # `patch` doesn't work as a decorator with generator functions so we
        # use `with`
        with patch.object(sublime, 'set_timeout_async', sublime.set_timeout):
            messages = []

            def work(message, worktime=None):
                if worktime:
                    time.sleep(worktime)
                messages.append(message)

            def sub_task():
                run_in_worker(work, 2, 0.5)  # add task (D)

            def uut():
                run_in_worker(work, 1, 0.3)    # add task (A)
                run_in_worker(sub_task)      # add task (B)

            uut()
            # task queue now: (A)..(B)

            yield  # add task (C) and wait for (C)
            #        (A) runs, (B) runs and adds task (D), (C) resolves
            expected = [1]
            self.assertEqual(messages, expected)
            # task queue now: (D)
            yield  # add task (E) and wait for it
            #        (D) runs and (E) resolves
            expected = [1, 2]
            self.assertEqual(messages, expected)
