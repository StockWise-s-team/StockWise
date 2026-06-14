import asyncio
from collections import defaultdict, deque
from time import monotonic
from typing import Protocol

from app.config import settings


class RateLimiter(Protocol):
    async def allow(self, key: str) -> bool:
        ...


class InMemoryRateLimiter:
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def allow(self, key: str) -> bool:
        async with self._lock:
            now = monotonic()
            requests = self._requests[key]
            while requests and requests[0] <= now - 60:
                requests.popleft()
            if len(requests) >= self.requests_per_minute:
                return False
            requests.append(now)
            return True


class RedisRateLimiter:
    def __init__(self, requests_per_minute: int):
        from redis.asyncio import Redis

        self.requests_per_minute = requests_per_minute
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def allow(self, key: str) -> bool:
        bucket = f"stockwise:advisor:rate:{key}"
        count = await self.redis.incr(bucket)
        if count == 1:
            await self.redis.expire(bucket, 60)
        return count <= self.requests_per_minute


class FallbackRateLimiter:
    def __init__(self, primary: RateLimiter, fallback: RateLimiter):
        self.primary = primary
        self.fallback = fallback

    async def allow(self, key: str) -> bool:
        try:
            return await self.primary.allow(key)
        except Exception:
            return await self.fallback.allow(key)


def create_rate_limiter() -> RateLimiter:
    fallback = InMemoryRateLimiter(settings.AI_RATE_LIMIT_PER_MINUTE)
    if not settings.AI_REDIS_RATE_LIMIT_ENABLED:
        return fallback
    return FallbackRateLimiter(RedisRateLimiter(settings.AI_RATE_LIMIT_PER_MINUTE), fallback)
