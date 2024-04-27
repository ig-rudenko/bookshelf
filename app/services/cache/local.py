import pickle
from datetime import datetime, timedelta
from typing import TypedDict, Any, Optional

from app.services.deco import singleton
from .base import AbstractCache
from .logger import logger


class _ValueType(TypedDict):
    data: Any
    expires: datetime


@singleton
class InMemoryCache(AbstractCache):
    """Кэш данных в памяти."""

    def __init__(self) -> None:
        self._cache: dict[str, _ValueType] = {}

    async def get(self, key: str) -> Optional[Any]:
        logger.debug(f"Get from cache %s", key)

        if value := self._cache.get(key, None):
            if value["expires"] > datetime.now():
                return pickle.loads(value["data"])
            else:
                await self.delete(key)
        return None

    async def set(self, key: str, value: Any, timeout: int) -> None:
        logger.debug(f"Set to cache %s", key)

        self._cache[key] = {
            "data": pickle.dumps(value),
            "expires": datetime.now() + timedelta(seconds=timeout),
        }

    async def delete(self, key: str) -> None:
        logger.debug(f"Delete_ from cache %s", key)
        self._cache.pop(key, None)

    async def delete_namespace(self, prefix: str) -> None:
        logger.debug(f"Delete namespace from cache %s", prefix)
        for key in list(self._cache.keys()):
            if key.startswith(prefix):
                self._cache.pop(key, None)
