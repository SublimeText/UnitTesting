import asyncio

from unittest import skipIf
from unittesting import IsolatedAsyncioTestCase


async def a_coro():
    return 1 + 1


class MyAsyncTestCase(IsolatedAsyncioTestCase):
    async def test_something(self):
        result = await a_coro()
        await asyncio.sleep(1)
        self.assertEqual(result, 2)
