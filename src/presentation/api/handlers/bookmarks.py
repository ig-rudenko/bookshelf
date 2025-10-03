from fastapi import APIRouter, Depends, status

from src.application.books.commands import UpdateFavoriteCommand, UpdateReadCommand
from src.application.books.handlers import BookmarksCommandHandler, BookmarksQueryHandler
from src.application.users.dto import UserDTO
from src.domain.books.entities import BookmarksQueryFilter

from ..auth import get_current_user
from ..dependencies import get_bookmark_command_handler, get_bookmark_query_handler
from ..schemas.books import BooksSchemaPaginated
from .queries import PaginatorQuery, paginator_query

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.get("/favorite", status_code=status.HTTP_200_OK, response_model=BooksSchemaPaginated)
async def get_favorite_books_view(
    paginator: PaginatorQuery = Depends(paginator_query),
    user: UserDTO = Depends(get_current_user),
    bookmark_query_handler: BookmarksQueryHandler = Depends(get_bookmark_query_handler),
):
    books, total = await bookmark_query_handler.handle_get_favorite_books(
        BookmarksQueryFilter(user_id=user.id, page=paginator.page, page_size=paginator.per_page)
    )

    return BooksSchemaPaginated.from_books_dto(
        books=books,
        total_count=total,
        current_page=paginator.page,
        per_page=paginator.per_page,
    )


@router.get("/favorite/count", status_code=status.HTTP_200_OK, response_model=int)
async def get_favorite_books_count_view(
    user: UserDTO = Depends(get_current_user),
    bookmark_query_handler: BookmarksQueryHandler = Depends(get_bookmark_query_handler),
):
    return await bookmark_query_handler.handle_get_favorite_books_count(user.id)


@router.get("/read", status_code=status.HTTP_200_OK, response_model=BooksSchemaPaginated)
async def get_read_books_view(
    paginator: PaginatorQuery = Depends(paginator_query),
    user: UserDTO = Depends(get_current_user),
    bookmark_query_handler: BookmarksQueryHandler = Depends(get_bookmark_query_handler),
):
    books, total = await bookmark_query_handler.handle_get_read_books(
        BookmarksQueryFilter(user_id=user.id, page=paginator.page, page_size=paginator.per_page)
    )

    return BooksSchemaPaginated.from_books_dto(
        books=books,
        total_count=total,
        current_page=paginator.page,
        per_page=paginator.per_page,
    )


@router.get("/read/count", status_code=status.HTTP_200_OK, response_model=int)
async def get_read_books_count_view(
    user: UserDTO = Depends(get_current_user),
    bookmark_query_handler: BookmarksQueryHandler = Depends(get_bookmark_query_handler),
):
    return await bookmark_query_handler.handle_get_read_books_count(user.id)


@router.post("/{book_id}/favorite", status_code=status.HTTP_200_OK)
async def mark_book_favorite(
    book_id: int,
    user: UserDTO = Depends(get_current_user),
    handler: BookmarksCommandHandler = Depends(get_bookmark_command_handler),
):
    await handler.handle_update_book_favorite(
        UpdateFavoriteCommand(book_id=book_id, user_id=user.id, favorite=True)
    )


@router.delete("/{book_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_book_favorite(
    book_id: int,
    user: UserDTO = Depends(get_current_user),
    handler: BookmarksCommandHandler = Depends(get_bookmark_command_handler),
):
    await handler.handle_update_book_favorite(
        UpdateFavoriteCommand(book_id=book_id, user_id=user.id, favorite=False)
    )


@router.post("/{book_id}/read", status_code=status.HTTP_200_OK)
async def mark_book_read(
    book_id: int,
    user: UserDTO = Depends(get_current_user),
    handler: BookmarksCommandHandler = Depends(get_bookmark_command_handler),
):
    await handler.handle_update_book_read(
        UpdateReadCommand(book_id=book_id, user_id=user.id, read=False),
    )


@router.delete("/{book_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_book_read(
    book_id: int,
    user: UserDTO = Depends(get_current_user),
    handler: BookmarksCommandHandler = Depends(get_bookmark_command_handler),
):
    await handler.handle_update_book_read(
        UpdateReadCommand(book_id=book_id, user_id=user.id, read=False),
    )
