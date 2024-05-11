import pickle
from typing import Optional, Any

from loguru import logger
from redis.asyncio import Redis

from app.services.deco import singleton
from .base import AbstractCache


@singleton
class RedisCache(AbstractCache):
    """Кэш данных в Redis."""

    def __init__(self, host: str, port: int, db: int, password: Optional[str] = None) -> None:
        self._redis: Redis = Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=2,
            socket_connect_timeout=2,
        )

    async def get(self, key: str) -> Optional[Any]:
        logger.debug(f"Get from cache {key}", key=key)

        value = await self._redis.get(key)
        if value is not None:
            return pickle.loads(value)
        return None

    async def set(self, key: str, value: Any, expire: int) -> None:
        logger.debug(f"Set to cache {key}", key=key)

        await self._redis.set(key, pickle.dumps(value), ex=expire)

    async def delete(self, key: str) -> None:
        logger.debug(f"Delete_ from cache {key}", key=key)
        await self._redis.delete(key)

    async def clear(self) -> None:
        logger.debug("Clear cache")
        await self._redis.flushdb(asynchronous=True)

    async def delete_namespace(self, prefix: str) -> None:
        logger.debug(f"Delete namespace from cache {prefix}", prefix=prefix)
        async for key in self._redis.scan_iter(f"{prefix}*"):
            await self._redis.delete(key)
