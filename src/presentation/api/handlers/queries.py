from dataclasses import dataclass
from typing import Annotated

from fastapi import Query


@dataclass(slots=True, kw_only=True)
class PaginatorQuery:
    page: int
    per_page: int


def paginator_query(
    page: Annotated[int, Query(gt=0, description="Номер страницы")] = 1,
    per_page: Annotated[
        int, Query(gte=1, le=100, alias="per-page", description="Количество элементов на странице")
    ] = 25,
) -> PaginatorQuery:
    return PaginatorQuery(page=page, per_page=per_page)
