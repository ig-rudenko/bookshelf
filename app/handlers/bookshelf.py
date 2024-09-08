from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.orm.session_manager import get_session
from app.schemas.bookshelf import (
    CreateUpdateBookshelfSchema,
    BookshelfSchema,
    BookshelfSchemaSchemaPaginated,
)
from app.services.aaa import get_current_user
from app.services.bookshelf import (
    QueryParams,
    get_filtered_bookshelves,
    create_bookshelf,
    delete_bookshelf,
    update_bookshelf,
)

router = APIRouter(prefix="/bookshelf", tags=["bookshelf"])


def books_query_params(
    search: str | None = Query(None, max_length=254, description="Поиск по названию и описанию"),
    page: int = Query(1, gt=0, description="Номер страницы"),
    per_page: int = Query(25, gte=1, alias="per-page", description="Количество элементов на странице"),
) -> QueryParams:
    """Параметры поиска по книгам."""

    return {
        "search": search,
        "page": page,
        "per_page": per_page,
    }


@router.get("", response_model=BookshelfSchemaSchemaPaginated)
async def get_bookshelf_list_api_view(
    query_params: QueryParams = Depends(books_query_params),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    return await get_filtered_bookshelves(session, query_params=query_params)


@router.post("", response_model=BookshelfSchema)
async def create_bookshelf_api_view(
    data: CreateUpdateBookshelfSchema,
    session: AsyncSession = Depends(get_session, use_cache=True),
    current_user: User = Depends(get_current_user),
):
    return await create_bookshelf(session, user_id=current_user.id, bookshelf_schema=data)


@router.put("/{bookshelf_id}", response_model=CreateUpdateBookshelfSchema)
async def update_bookshelf_api_view(
    bookshelf_id: int,
    data: CreateUpdateBookshelfSchema,
    session: AsyncSession = Depends(get_session, use_cache=True),
    user: User = Depends(get_current_user),
):
    return await update_bookshelf(session, bookshelf_id=bookshelf_id, user_id=user.id, bookshelf_schema=data)


@router.delete("/{bookshelf_id}", status_code=204)
async def delete_bookshelf_api_view(
    bookshelf_id: int,
    session: AsyncSession = Depends(get_session, use_cache=True),
    _: User = Depends(get_current_user),
):
    return await delete_bookshelf(session, bookshelf_id=bookshelf_id)
