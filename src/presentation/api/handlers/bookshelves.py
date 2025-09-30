from fastapi import APIRouter, Depends, Query

from src.application.bookshelves.commands import (
    BookshelfCreateCommand,
    BookshelfDeleteCommand,
    BookshelfUpdateCommand,
)
from src.application.bookshelves.handlers import BookshelfCommandHandler, BookshelfQueryHandler
from src.application.users.dto import UserDTO
from src.domain.bookshelves.entities import BookshelfFilter

from ..auth import get_current_user, get_user_or_none
from ..dependencies import get_bookshelf_command_handler, get_bookshelf_query_handler
from ..schemas.bookshelves import BookshelfSchema, BookshelfSchemaSchemaPaginated, CreateUpdateBookshelfSchema

router = APIRouter(prefix="/bookshelf", tags=["bookshelf"])


def books_query_params(
    search: str | None = Query(None, max_length=254, description="Поиск по названию и описанию"),
    private: bool | None = Query(None, description="Фильтр по приватности"),
    page: int = Query(1, gt=0, description="Номер страницы"),
    per_page: int = Query(25, gte=1, alias="per-page", description="Количество элементов на странице"),
) -> BookshelfFilter:
    """Параметры поиска по книгам."""

    return BookshelfFilter(
        search=search,
        page=page,
        page_size=per_page,
        is_private=private,
    )


@router.get("", response_model=BookshelfSchemaSchemaPaginated)
async def get_bookshelf_list_api_view(
    query_params: BookshelfFilter = Depends(books_query_params),
    current_user: UserDTO | None = Depends(get_user_or_none),
    bookshelf_handler: BookshelfQueryHandler = Depends(get_bookshelf_query_handler),
):
    query_params.viewer_id = current_user.id if current_user else None
    bookshelves, count = await bookshelf_handler.handle_filter(query_params)
    return BookshelfSchemaSchemaPaginated(
        bookshelves=[BookshelfSchema.model_validate(bookshelf) for bookshelf in bookshelves],
        total_count=count,
        current_page=query_params.page,
        per_page=query_params.page_size,
        max_pages=count // query_params.page_size + 1 if count % query_params.page_size else 0,
    )


@router.post("", response_model=BookshelfSchema)
async def create_bookshelf_api_view(
    data: CreateUpdateBookshelfSchema,
    current_user: UserDTO = Depends(get_current_user),
    handler: BookshelfCommandHandler = Depends(get_bookshelf_command_handler),
):
    bookshelf = await handler.handle_create(
        BookshelfCreateCommand(
            name=data.name,
            description=data.description,
            private=data.private,
            user=current_user,
            books=data.books,
        )
    )
    return BookshelfSchema.model_validate(bookshelf)


@router.get("/{bookshelf_id}", response_model=BookshelfSchema)
async def get_bookshelf_api_view(
    bookshelf_id: int,
    current_user: UserDTO | None = Depends(get_user_or_none),
    bookshelf_handler: BookshelfQueryHandler = Depends(get_bookshelf_query_handler),
):
    return await bookshelf_handler.handle_get(bookshelf_id, current_user.id if current_user else None)


@router.put("/{bookshelf_id}", response_model=CreateUpdateBookshelfSchema)
async def update_bookshelf_api_view(
    bookshelf_id: int,
    data: CreateUpdateBookshelfSchema,
    current_user: UserDTO = Depends(get_current_user),
    handler: BookshelfCommandHandler = Depends(get_bookshelf_command_handler),
):
    return await handler.handle_update(
        BookshelfUpdateCommand(
            id=bookshelf_id,
            user=current_user,
            name=data.name,
            description=data.description,
            private=data.private,
            books=data.books,
        )
    )


@router.delete("/{bookshelf_id}", status_code=204)
async def delete_bookshelf_api_view(
    bookshelf_id: int,
    current_user: UserDTO = Depends(get_current_user),
    handler: BookshelfCommandHandler = Depends(get_bookshelf_command_handler),
):
    await handler.handle_delete(
        BookshelfDeleteCommand(
            user=current_user,
            id=bookshelf_id,
        )
    )
