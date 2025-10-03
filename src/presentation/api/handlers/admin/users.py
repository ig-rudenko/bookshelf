from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status

from src.application.books.handlers import BookmarksQueryHandler, BookQueryHandler
from src.application.users.dto import UserDTO
from src.application.users.handlers import UserQueryHandler
from src.application.users.queries import UserFilterDTO
from src.domain.books.entities import BookmarksQueryFilter
from src.presentation.api.auth import superuser_required
from src.presentation.api.dependencies import (
    get_book_query_handler,
    get_bookmark_query_handler,
    get_user_query_handler,
)
from src.presentation.api.handlers.queries import PaginatorQuery, paginator_query
from src.presentation.api.schemas.books import BooksSchemaPaginated, BooksWithReadPagesPaginatedSchema
from src.presentation.api.schemas.users import UserDetailSchema, UserSchemaPaginated

router = APIRouter(prefix="/users")


def users_query_params(
    paginator: Annotated[PaginatorQuery, Depends(paginator_query)],
    sort_by: Annotated[str, Query(description="Сортировка", alias="sort-by")] = "id",
    sort_order: Annotated[
        Literal["asc", "desc"], Query(description="Направление сортировки", alias="sort-order")
    ] = "desc",
) -> UserFilterDTO:
    available_sort_fields = {
        "id": "id",
        "username": "username",
        "isSuperuser": "is_superuser",
        "isStaff": "is_staff",
        "firstName": "first_name",
        "lastName": "last_name",
        "email": "email",
        "dateJoin": "date_join",
        "favoritesCount": "favorites_count",
        "readCount": "read_count",
        "recentlyReadCount": "recently_read_count",
    }
    if sort_by and sort_by not in available_sort_fields:
        sort_by = "id"
    if sort_order not in ("asc", "desc"):
        raise ValueError("Неверное значение направления сортировки")

    return UserFilterDTO(
        sort_by=available_sort_fields[sort_by],
        sort_order=sort_order,
        page=paginator.page,
        per_page=paginator.per_page,
    )


@router.get("", response_model=UserSchemaPaginated)
async def get_users(
    query_params: Annotated[UserFilterDTO, Depends(users_query_params)],
    handler: Annotated[UserQueryHandler, Depends(get_user_query_handler)],
    _: Annotated[UserDTO, Depends(superuser_required)],
):
    """Возвращает всех пользователей."""
    users, count = await handler.handle_get_list(filter_=query_params)
    return UserSchemaPaginated(
        results=[UserDetailSchema.model_validate(user) for user in users],
        total_count=count,
        current_page=query_params.page,
        per_page=query_params.per_page,
        max_pages=(
            count // query_params.per_page
            if count % query_params.per_page
            else count // query_params.per_page + 1
        ),
    )


@router.get("/{user_id}/favorite", status_code=status.HTTP_200_OK, response_model=BooksSchemaPaginated)
async def get_favorite_books_view(
    user_id: int,
    paginator: Annotated[PaginatorQuery, Depends(paginator_query)],
    handler: Annotated[BookmarksQueryHandler, Depends(get_bookmark_query_handler)],
    _=Depends(superuser_required),
):
    """Возвращает избранные книги пользователя."""
    books, count = await handler.handle_get_favorite_books(
        BookmarksQueryFilter(
            user_id=user_id,
            page=paginator.page,
            page_size=paginator.per_page,
        )
    )
    return BooksSchemaPaginated.from_books_dto(
        books=books,
        total_count=count,
        current_page=paginator.page,
        per_page=paginator.per_page,
    )


@router.get("/{user_id}/read", status_code=status.HTTP_200_OK, response_model=BooksSchemaPaginated)
async def get_read_books_view(
    user_id: int,
    paginator: Annotated[PaginatorQuery, Depends(paginator_query)],
    handler: Annotated[BookmarksQueryHandler, Depends(get_bookmark_query_handler)],
    _=Depends(superuser_required),
):
    """Возвращает прочитанные книги пользователя."""
    books, count = await handler.handle_get_read_books(
        BookmarksQueryFilter(
            user_id=user_id,
            page=paginator.page,
            page_size=paginator.per_page,
        )
    )
    return BooksSchemaPaginated.from_books_dto(
        books=books,
        total_count=count,
        current_page=paginator.page,
        per_page=paginator.per_page,
    )


@router.get(
    "/{user_id}/last-viewed", status_code=status.HTTP_200_OK, response_model=BooksWithReadPagesPaginatedSchema
)
async def get_last_viewed_books_view(
    user_id: int,
    paginator: Annotated[PaginatorQuery, Depends(paginator_query)],
    query_handler: Annotated[BookQueryHandler, Depends(get_book_query_handler)],
    _=Depends(superuser_required),
):
    """Возвращает просмотренные книги пользователя с кол-вом просмотренных страниц."""
    result, count = await query_handler.handler_get_last_viewed_books(
        user_id, paginator.page, paginator.per_page
    )
    return BooksWithReadPagesPaginatedSchema.from_books_dto(
        books=result,
        total_count=count,
        current_page=paginator.page,
        per_page=paginator.per_page,
    )
