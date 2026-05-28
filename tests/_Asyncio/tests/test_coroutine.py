import asyncio

from unittesting import AsyncViewTestCase


async def a_coro(test: MyAsyncTestCase):
    await asyncio.sleep(1.0)
    test.setText("Modified Content")


class MyAsyncTestCase(AsyncViewTestCase):

    async def setUp(self):
        self.setText("Initial Content")

    async def tearDown(self):
        self.setText("")

    async def test_setup_completed(self):
        self.assertViewContentsEqual("Initial Content")

    async def test_coroutine(self):
        await a_coro(self)
        self.assertViewContentsEqual("Modified Content")
