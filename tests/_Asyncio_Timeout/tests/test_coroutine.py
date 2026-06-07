import asyncio

from unittesting import AsyncTestCase


async def a_coro(test):
    await asyncio.sleep(1.0)


class MyAsyncTestCaseA(AsyncTestCase):
    timeout_ms = 100

    async def test_coroutine_class_timeout(self):
        await a_coro(self)


class MyAsyncTestCaseB(AsyncTestCase):
    async def test_coroutine_local_timeout(self, timeout_ms=100):
        await a_coro(self)
