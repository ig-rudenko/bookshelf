from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.application.books.commands import UpdateFavoriteCommand, UpdateReadCommand
from src.application.books.handlers import BookmarksCommandHandler, BookmarksQueryHandler
from src.application.users.dto import UserDTO
from src.domain.books.entities import BookFilter, BookmarksQueryFilter

from ..auth import get_current_user
from ..dependencies import get_bookmark_command_handler, get_bookmark_query_handler
from ..schemas.books import BooksSchemaPaginated
from .books import books_query_params

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.get("/favorite", status_code=status.HTTP_200_OK, response_model=BooksSchemaPaginated)
async def get_favorite_books_view(
    query_params: Annotated[BookFilter, Depends(books_query_params)],
    user: Annotated[UserDTO, Depends(get_current_user)],
    bookmark_query_handler: Annotated[BookmarksQueryHandler, Depends(get_bookmark_query_handler)],
):
    books, total = await bookmark_query_handler.handle_get_favorite_books(
        BookmarksQueryFilter(user_id=user.id, page=query_params.page, page_size=query_params.page_size,
                             book_filter=query_params)
    )

    return BooksSchemaPaginated.from_books_dto(
        books=books,
        total_count=total,
        current_page=query_params.page,
        per_page=query_params.page_size,
    )


@router.get("/favorite/count", status_code=status.HTTP_200_OK, response_model=int)
async def get_favorite_books_count_view(
    user: Annotated[UserDTO, Depends(get_current_user)],
    bookmark_query_handler: Annotated[BookmarksQueryHandler, Depends(get_bookmark_query_handler)],
):
    return await bookmark_query_handler.handle_get_favorite_books_count(user.id)


@router.get("/read", status_code=status.HTTP_200_OK, response_model=BooksSchemaPaginated)
async def get_read_books_view(
    query_params: Annotated[BookFilter, Depends(books_query_params)],
    user: Annotated[UserDTO, Depends(get_current_user)],
    bookmark_query_handler: Annotated[BookmarksQueryHandler, Depends(get_bookmark_query_handler)],
):
    books, total = await bookmark_query_handler.handle_get_read_books(
        BookmarksQueryFilter(user_id=user.id, page=query_params.page, page_size=query_params.page_size,
                             book_filter=query_params)
    )

    return BooksSchemaPaginated.from_books_dto(
        books=books,
        total_count=total,
        current_page=query_params.page,
        per_page=query_params.page_size,
    )


@router.get("/read/count", status_code=status.HTTP_200_OK, response_model=int)
async def get_read_books_count_view(
    user: Annotated[UserDTO, Depends(get_current_user)],
    bookmark_query_handler: Annotated[BookmarksQueryHandler, Depends(get_bookmark_query_handler)],
):
    return await bookmark_query_handler.handle_get_read_books_count(user.id)


@router.post("/{book_id}/favorite", status_code=status.HTTP_200_OK)
async def mark_book_favorite(
    book_id: int,
    user: Annotated[UserDTO, Depends(get_current_user)],
    handler: Annotated[BookmarksCommandHandler, Depends(get_bookmark_command_handler)],
):
    await handler.handle_update_book_favorite(
        UpdateFavoriteCommand(book_id=book_id, user_id=user.id, favorite=True)
    )


@router.delete("/{book_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_book_favorite(
    book_id: int,
    user: Annotated[UserDTO, Depends(get_current_user)],
    handler: Annotated[BookmarksCommandHandler, Depends(get_bookmark_command_handler)],
):
    await handler.handle_update_book_favorite(
        UpdateFavoriteCommand(book_id=book_id, user_id=user.id, favorite=False)
    )


@router.post("/{book_id}/read", status_code=status.HTTP_200_OK)
async def mark_book_read(
    book_id: int,
    user: Annotated[UserDTO, Depends(get_current_user)],
    handler: Annotated[BookmarksCommandHandler, Depends(get_bookmark_command_handler)],
):
    await handler.handle_update_book_read(
        UpdateReadCommand(book_id=book_id, user_id=user.id, read=True),
    )


@router.delete("/{book_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_book_read(
    book_id: int,
    user: Annotated[UserDTO, Depends(get_current_user)],
    handler: Annotated[BookmarksCommandHandler, Depends(get_bookmark_command_handler)],
):
    await handler.handle_update_book_read(
        UpdateReadCommand(book_id=book_id, user_id=user.id, read=False),
    )
