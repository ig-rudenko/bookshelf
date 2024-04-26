from typing import TypeVar, Any, Awaitable, Self

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.util import greenlet_spawn

# Default naming convention for all indexes and constraints
# See why this is important and how it would save your time:
# https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}

_T = TypeVar("_T", bound=Any)


class AwaitAttrs:
    """
    Базовый класс для классов ORM, предоставляющий доступ к атрибутам с ожиданием (awaitable).
    Добавляет функциональность для асинхронного доступа к атрибутам.
    """

    class _AwaitAttrGetitem:
        """Внутренний класс для реализации асинхронного доступа к атрибутам."""

        __slots__ = "_instance"

        def __init__(self, _instance: Any):
            self._instance = _instance

        def __getattr__(self, name: str) -> Awaitable[Any]:
            return greenlet_spawn(getattr, self._instance, name)

    @property
    def await_attr(self) -> Self:
        """
        Предоставляет доступ к атрибутам объекта с ожиданием.
        Возвращает объект `_AwaitAttrGetitem`, который перехватывает
        обращение к атрибутам и запускает их получение в отдельной
        greenlet-функции.
        """
        return AwaitAttrs._AwaitAttrGetitem(self)  # type: ignore


class OrmBase(AwaitAttrs, DeclarativeBase):
    """
    Базовый класс для моделей SQLAlchemy с поддержкой асинхронного доступа к атрибутам.

    Класс `OrmBase` наследуется от `AwaitAttrs` и `DeclarativeBase`.
    Он использует `DeclarativeBase` для создания моделей ORM
    и добавляет функциональность `AwaitAttrs` для асинхронного доступа к атрибутам.
    """

    metadata = MetaData(naming_convention=convention)  # type: ignore
