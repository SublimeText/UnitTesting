from unittesting import ViewTestCase


class TestHelloWorld(ViewTestCase):

    def test_hello_world(self):
        self.setText("hello world")
        first_row = self.getRowText(0)
        self.assertEqual(first_row, "hello world!")
