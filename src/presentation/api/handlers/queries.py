from dataclasses import dataclass

from fastapi import Query


@dataclass(slots=True, kw_only=True)
class PaginatorQuery:
    page: int
    per_page: int


def paginator_query(
    page: int = Query(1, gt=0, description="Номер страницы"),
    per_page: int = Query(
        25, gte=1, le=100, alias="per-page", description="Количество элементов на странице"
    ),
) -> PaginatorQuery:
    return PaginatorQuery(page=page, per_page=per_page)
