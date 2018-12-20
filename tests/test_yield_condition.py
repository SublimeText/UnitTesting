from unittesting import DeferrableTestCase


class TestYieldConditionsHandlingInDeferredTestCase(DeferrableTestCase):
    def test_reraises_errors_raised_in_conditions(self):
        try:
            yield lambda: 1 / 0
            self.fail('Did not reraise the exception from the condition')
        except ZeroDivisionError:
            pass
        except Exception:
            self.fail('Did not throw the original exception')

    def test_returns_condition_value(self):
        rv = yield lambda: 'Hans Peter'

        self.assertEqual(rv, 'Hans Peter')

    def test_handle_condition_timeout_as_failure(self):
        try:
            yield {
                'condition': lambda: True is False,
                'timeout': 100
            }
            self.fail('Unmet condition should have thrown')
        except TimeoutError as e:
            self.assertEqual(
                str(e),
                'Condition not fulfilled within 0.10 seconds'
            )
