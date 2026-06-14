import pytest

from app.services.rate_limiter import FallbackRateLimiter, InMemoryRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_blocks_after_limit():
    limiter = InMemoryRateLimiter(2)
    assert await limiter.allow("user") is True
    assert await limiter.allow("user") is True
    assert await limiter.allow("user") is False


class FailingLimiter:
    async def allow(self, key):
        raise RuntimeError("redis down")


@pytest.mark.asyncio
async def test_rate_limiter_falls_back_when_redis_is_unavailable():
    limiter = FallbackRateLimiter(FailingLimiter(), InMemoryRateLimiter(1))
    assert await limiter.allow("user") is True
    assert await limiter.allow("user") is False
