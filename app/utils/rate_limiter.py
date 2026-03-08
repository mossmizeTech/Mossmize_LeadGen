"""
Token-bucket rate limiter for controlling API and crawl request rates.
"""

import asyncio
import time


class RateLimiter:
    """
    Async token-bucket rate limiter.

    Usage:
        limiter = RateLimiter(max_per_second=10)
        await limiter.acquire()  # blocks if rate exceeded
    """

    def __init__(self, max_per_second: float):
        self.max_per_second = max_per_second
        self.min_interval = 1.0 / max_per_second
        self._last_time = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a request slot is available."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_time
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                await asyncio.sleep(wait_time)
            self._last_time = time.monotonic()
