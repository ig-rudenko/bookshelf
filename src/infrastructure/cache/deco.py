from collections.abc import Callable
from functools import wraps
from typing import Any

from src.infrastructure.dependencies import get_cache


def cached(
    timeout: int,
    key: str | None = None,
    variable_positions: list[int] | None = None,
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
