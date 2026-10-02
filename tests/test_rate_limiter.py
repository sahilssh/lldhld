import unittest
import time
import threading

class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = float(capacity)
        self.refill_rate = refill_rate_per_sec
        self.tokens = float(capacity)
        self.last_refill_timestamp = time.time()
        self.lock = threading.Lock()

    def allow_request(self, tokens_needed: int = 1) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill_timestamp
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill_timestamp = now

            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            return False

class TestRateLimiter(unittest.TestCase):
    def test_token_bucket_burst_and_throttle(self):
        limiter = TokenBucketRateLimiter(capacity=3, refill_rate_per_sec=10.0)
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        # 4th immediate request exceeds capacity
        self.assertFalse(limiter.allow_request())

        # Wait 0.25 seconds (should refill ~2.5 tokens)
        time.sleep(0.25)
        self.assertTrue(limiter.allow_request())

if __name__ == "__main__":
    unittest.main()
