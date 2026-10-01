# ⏱️ Low-Level Design: Rate Limiter Algorithms & Implementations

Rate limiters protect servers against abuse, DoS attacks, and resource starvation. In LLD interviews, candidates are expected to implement one or more algorithms and explain trade-offs.

---

## 📊 Algorithm Comparison

| Algorithm | Memory Consumption | Burst Handling | Implementation Complexity | Best Used For |
|---|---|---|---|---|
| **Token Bucket** | Minimal ($O(1)$ per client) | ✅ Yes (allows bursts up to capacity) | Low | General REST APIs, AWS API Gateway |
| **Leaky Bucket** | Minimal ($O(1)$) | ❌ No (smooths traffic to constant rate) | Medium | E-commerce checkout, payment queues |
| **Fixed Window Counter** | Minimal ($O(1)$) | ⚠️ Edge case: 2x burst across window boundaries | Very Low | Simple coarse-grained quotas (e.g. daily) |
| **Sliding Window Log** | High ($O(N)$ where $N$ = request count) | ✅ Strict, accurate | High | Critical low-volume security/auth endpoints |
| **Sliding Window Counter** | Low ($O(1)$) | ✅ Smooths boundary bursts, low memory | Medium | High-scale production systems (Cloudflare) |

---

## 1. Token Bucket Implementation (Thread-Safe)

### How it works:
* A bucket holds up to $C$ tokens.
* Tokens are added at a constant fill rate $R$ per second.
* Every request requires 1 token. If tokens are available, allow the request; otherwise, drop/reject.
* **Lazy Token Generation**: Instead of a background timer, compute tokens dynamically based on elapsed time:
  $$\text{new\_tokens} = (\text{now} - \text{last\_refill\_time}) \times \text{refill\_rate}$$

```python
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
            
            # Add newly accrued tokens
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill_timestamp = now

            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            return False

# Usage
limiter = TokenBucketRateLimiter(capacity=5, refill_rate_per_sec=1.0)
for i in range(7):
    allowed = limiter.allow_request()
    print(f"Req {i + 1}: {'ALLOWED' if allowed else 'THROTTLED'}")
```

---

## 2. Sliding Window Counter Implementation

Combines the low memory footprint of Fixed Window with the accuracy of Sliding Window Log by weighting requests from the previous and current window:

$$\text{Estimated Requests} = \text{Current Window Count} + \text{Previous Window Count} \times \left(1 - \frac{\text{Current Window Progress}}{\text{Window Size}}\right)$$

```python
import time
import threading

class SlidingWindowCounterRateLimiter:
    def __init__(self, limit: int, window_size_seconds: float):
        self.limit = limit
        self.window_size = window_size_seconds
        self.current_window_start = int(time.time() // self.window_size)
        self.current_count = 0
        self.previous_count = 0
        self.lock = threading.Lock()

    def allow_request(self) -> bool:
        with self.lock:
            now = time.time()
            window_idx = int(now // self.window_size)

            if window_idx > self.current_window_start:
                if window_idx == self.current_window_start + 1:
                    self.previous_count = self.current_count
                else:
                    self.previous_count = 0
                self.current_count = 0
                self.current_window_start = window_idx

            # Weight calculation
            progress = (now % self.window_size) / self.window_size
            estimated_requests = self.current_count + self.previous_count * (1.0 - progress)

            if estimated_requests < self.limit:
                self.current_count += 1
                return True
            return False
```
