import logging
import pickle
from abc import abstractmethod, ABC
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional, TypedDict, Callable

from redis.asyncio import Redis

from app.services.deco import singleton
from app.settings import settings

logger = logging.getLogger(__name__)


class AbstractCache(ABC):
    """Абстрактный класс для реализации кеша данных."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Получает значение из кеша по ключу."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, timeout: int) -> None:
        """Записывает значение в кеш по ключу и устанавливает таймаут для удаления."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Удаляет значение из кеша по ключу."""
        pass

    @abstractmethod
    async def delete_namespace(self, prefix: str) -> None:
        """Удаляет все ключи с указанным префиксом"""
        pass


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
        logger.debug(f"Get from cache %s", key)

        value = await self._redis.get(key)
        if value is not None:
            return pickle.loads(value)
        return None

    async def set(self, key: str, value: Any, expire: int) -> None:
        logger.debug(f"Set to cache %s", key)

        await self._redis.set(key, pickle.dumps(value), ex=expire)

    async def delete(self, key: str) -> None:
        logger.debug(f"Delete_ from cache %s", key)
        await self._redis.delete(key)

    async def clear(self) -> None:
        logger.debug("Clear cache")
        await self._redis.flushdb(asynchronous=True)

    async def delete_namespace(self, prefix: str) -> None:
        logger.debug(f"Delete namespace from cache %s", prefix)
        async for key in self._redis.scan_iter(f"{prefix}*"):
            await self._redis.delete(key)


def get_cache() -> AbstractCache:
    """Возвращает кэш в зависимости от настроек приложения"""
    if settings.REDIS_HOST:
        return RedisCache(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
    else:
        return InMemoryCache()


def cached(
    timeout: int,
    key: Optional[str] = None,
    variable_positions: Optional[list[int]] = None,
    delimiter: str = ":",
) -> Callable[..., Any]:
    """
    Декоратор кэширования функции.

    :param timeout: Время жизни кэш.
    :param key: Ключ кэша, если не указан будет взято имя функции.
    :param variable_positions: Список позиций аргументов, которые будут добавлены в ключ через str().
    :param delimiter: Разделитель позиций аргументов.

    :return: Декоратор функции.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key: str = key if key is not None else func.__name__

            # Добавляем в название ключа значение аргументов
            if variable_positions is not None:
                for pos in variable_positions:
                    if len(args) >= pos:
                        cache_key += delimiter + str(args[pos - 1])
                    elif len(kwargs) >= pos - len(args):
                        values = list(kwargs.values())
                        cache_key += delimiter + str(values[pos - len(args) - 1])

            cache = get_cache()
            value = await cache.get(cache_key)
            if value is not None:
                return value
            value = await func(*args, **kwargs)
            await cache.set(cache_key, value, timeout)
            return value

        return wrapper

    return decorator
