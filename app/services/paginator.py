from typing import TypeVar, TypedDict

from fastapi import Query
from sqlalchemy import Select

Q = TypeVar("Q", bound=Select)


class PaginatorQuery(TypedDict):
    page: int
    per_page: int


def paginate(query: Q, page: int, per_page: int) -> Q:
    """Paginate a query"""
    return query.offset((page - 1) * per_page).limit(per_page)


def paginator_query(
    page: int = Query(1, gt=0, description="Номер страницы"),
    per_page: int = Query(25, gte=1, le=100, alias="per-page", description="Количество элементов на странице"),
) -> PaginatorQuery:
    """Возвращает словарь с параметрами запроса для paginate"""
    return {
        "page": page,
        "per_page": per_page,
    }
