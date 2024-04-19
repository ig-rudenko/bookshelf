from typing import TypeVar

from sqlalchemy import Select

Q = TypeVar("Q", bound=Select)


def paginate(query: Q, page: int, per_page: int) -> Q:
    """Paginate a query"""
    return query.offset((page - 1) * per_page).limit(per_page)
