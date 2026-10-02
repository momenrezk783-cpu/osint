import unittest
import unittest.mock
from src.core.circuit_breaker import CircuitBreaker, CircuitState

class TestCircuitBreaker(unittest.TestCase):
    def test_initial_state(self):
        cb = CircuitBreaker()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.allow_request())

    def test_record_failure_below_threshold(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.allow_request())

    def test_record_failure_reaches_threshold(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.state, CircuitState.OPEN)
        self.assertFalse(cb.allow_request())

    @unittest.mock.patch('time.time')
    def test_recovery_timeout(self, mock_time):
        mock_time.return_value = 1000.0
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=30)
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.state, CircuitState.OPEN)
        self.assertFalse(cb.allow_request())

        # Advance time past recovery timeout
        mock_time.return_value = 1035.0

        self.assertTrue(cb.allow_request())
        self.assertEqual(cb.state, CircuitState.HALF_OPEN)

    def test_record_success_resets(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.state, CircuitState.OPEN)

        cb.record_success()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertEqual(cb.failure_count, 0)
        self.assertTrue(cb.allow_request())

if __name__ == '__main__':
    unittest.main()
