import redis

from core.settings import settings


redis_client = redis.Redis().from_url(
    settings.redis_url  # type:ignore[arg-type]
)
