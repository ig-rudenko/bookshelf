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
    class _AwaitAttrGetitem:
        __slots__ = "_instance"

        def __init__(self, _instance: Any):
            self._instance = _instance

        def __getattr__(self, name: str) -> Awaitable[Any]:
            return greenlet_spawn(getattr, self._instance, name)

    @property
    def await_attr(self) -> Self:
        """provide awaitable attribute access"""
        return AwaitAttrs._AwaitAttrGetitem(self)  # type: ignore


class OrmBase(AwaitAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention=convention)  # type: ignore
