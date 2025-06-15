from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.handlers.admin.base import superuser_required
from app.orm.session_manager import get_session
from app.schemas.books import BooksSchemaPaginated, BooksWithReadPagesPaginatedSchema
from app.schemas.users import UserSchemaPaginated
from app.services.bookmarks import get_favorite_books, get_read_books
from app.services.paginator import paginator_query
from app.services.pdf_history import get_last_viewed_books
from app.services.users import get_all_users

router = APIRouter(prefix="/users")


@router.get("", response_model=UserSchemaPaginated)
async def get_users(
    query_params: dict = Depends(paginator_query),
    session: AsyncSession = Depends(get_session, use_cache=True),
    _=Depends(superuser_required),
):
    """Возвращает всех пользователей."""
    return await get_all_users(session=session, paginator=query_params)


@router.get("/{user_id}/favorite", status_code=status.HTTP_200_OK, response_model=BooksSchemaPaginated)
async def get_favorite_books_view(
    user_id: int,
    paginator: dict = Depends(paginator_query),
    session: AsyncSession = Depends(get_session),
    _=Depends(superuser_required),
):
    """Возвращает избранные книги пользователя."""
    return await get_favorite_books(session=session, user_id=user_id, paginator=paginator)


@router.get("/{user_id}/read", status_code=status.HTTP_200_OK, response_model=BooksSchemaPaginated)
async def get_read_books_view(
    user_id: int,
    paginator: dict = Depends(paginator_query),
    session: AsyncSession = Depends(get_session),
    _=Depends(superuser_required),
):
    """Возвращает прочитанные книги пользователя."""
    return await get_read_books(session=session, user_id=user_id, paginator=paginator)


@router.get(
    "/{user_id}/last-viewed", status_code=status.HTTP_200_OK, response_model=BooksWithReadPagesPaginatedSchema
)
async def get_last_viewed_books_view(
    user_id: int,
    paginator: dict = Depends(paginator_query),
    session: AsyncSession = Depends(get_session),
    _=Depends(superuser_required),
):
    """Возвращает просмотренные книги пользователя с кол-вом просмотренных страниц."""
    return await get_last_viewed_books(session, user_id, paginator)
