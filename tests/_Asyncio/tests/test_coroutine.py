import asyncio

from unittesting import AsyncViewTestCase


async def a_coro(test):
    await asyncio.sleep(1.0)
    test.setText("Modified Content")


class MyAsyncTestCaseA(AsyncViewTestCase):

    test_class_initiated = 0

    @classmethod
    async def setUpClass(cls):
        assert cls.test_class_initiated == 0
        cls.test_class_initiated = 1

    @classmethod
    async def tearDownClass(cls):
        cls.test_class_initiated = 2

    async def setUp(self):
        self.setText("Initial Content")

    async def tearDown(self):
        self.setText("")

    async def test_class_setup_completed(self):
        self.assertEqual(self.test_class_initiated, 1)

    async def test_setup_completed(self):
        self.assertViewContentsEqual("Initial Content")

    async def test_coroutine(self):
        await a_coro(self)
        self.assertViewContentsEqual("Modified Content")


class MyAsyncTestCaseB(AsyncViewTestCase):

    async def test_class_setup_completed(self):
        self.assertEqual(MyAsyncTestCaseA.test_class_initiated, 2)
