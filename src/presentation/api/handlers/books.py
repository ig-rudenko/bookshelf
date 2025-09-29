from fastapi import APIRouter, Depends, Query

from src.application.books.handlers import BookQueryHandler
from src.application.users.dto import UserDTO
from src.presentation.api.auth import get_user_or_none, get_current_user
from src.presentation.api.dependencies import get_book_query_handler
from src.presentation.api.handlers.queries import paginator_query, PaginatorQuery
from src.presentation.api.schemas.books import (
    BookSchema,
    BooksWithReadPagesPaginatedSchema,
    BookWithReadPagesSchema,
)

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/recent", response_model=list[BookSchema])
async def get_recent_books_view(
    current_user: UserDTO | None = Depends(get_user_or_none),
    query_handler: BookQueryHandler = Depends(get_book_query_handler),
):
    """Последние 25 добавленных книг."""
    books = await query_handler.handle_get_recent_books(current_user.id if current_user else None)
    return books


@router.get("/publishers", response_model=list[str])
async def get_publishers_view(
    name: str | None = Query(None, description="Издательство"),
    current_user: UserDTO | None = Depends(get_user_or_none),
    query_handler: BookQueryHandler = Depends(get_book_query_handler),
):
    """Поиск издательств по названию."""
    return await query_handler.handle_get_publishers(
        search=name, user_id=current_user.id if current_user else None
    )


@router.get("/authors", response_model=list[str])
async def get_authors_view(
    name: str | None = Query(None, description="Авторы книги"),
    current_user: UserDTO | None = Depends(get_user_or_none),
    query_handler: BookQueryHandler = Depends(get_book_query_handler),
):
    """Поиск авторов по названию."""
    return await query_handler.handle_get_authors(
        search=name, user_id=current_user.id if current_user else None
    )


@router.get("/last-viewed", response_model=BooksWithReadPagesPaginatedSchema)
async def get_last_viewed_books_view(
    paginator: PaginatorQuery = Depends(paginator_query),
    user: UserDTO = Depends(get_current_user),
    query_handler: BookQueryHandler = Depends(get_book_query_handler),
):
    """Возвращает просмотренные книги пользователя с кол-вом просмотренных страниц."""
    result, count = await query_handler.handler_get_last_viewed_books(
        user.id, paginator.page, paginator.per_page
    )
    return BooksWithReadPagesPaginatedSchema(
        books=[BookWithReadPagesSchema.model_validate(book) for book in result],
        total_count=count,
        current_page=paginator.page,
        max_pages=(
            count // paginator.per_page
            if count % paginator.per_page == 0
            else count // paginator.per_page + 1
        ),
        per_page=paginator.per_page,
    )
