from typing import Optional

from fastapi import APIRouter, UploadFile, HTTPException, Depends, status, Query
from fastapi.responses import StreamingResponse
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.media_storage import get_storage
from app.models import User
from app.orm.session_manager import get_session
from app.schemas.books import (
    BookSchema,
    CreateBookSchema,
    BooksSchemaPaginated,
    BookSchemaDetail,
    BookSchemaWithDesc,
    BooksWithReadPagesPaginatedSchema,
)
from app.services.aaa import get_current_user, get_user_or_none
from app.services.books import (
    set_file,
    QueryParams,
    get_filtered_books,
    delete_book,
    get_recent_books,
    delete_recent_books_cache,
    get_book,
    get_book_detail,
    create_book,
    update_book,
)
from app.services.celery import create_book_preview_task
from app.services.paginator import paginator_query
from app.services.pdf_history import get_last_viewed_books
from app.services.permissions import check_book_owner_permission
from app.services.publishers import get_publishers, get_authors

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/recent", response_model=list[BookSchema])
async def get_recent_books_view(
    session: AsyncSession = Depends(get_session, use_cache=True),
    current_user: Optional[User] = Depends(get_user_or_none),
):
    """Последние 25 добавленных книг."""
    return await get_recent_books(session, limit=25, user_id=current_user.id if current_user else None)


@router.get("/publishers", response_model=list[str])
async def get_publishers_view(
    name: str | None = Query(None, description="Издательство"),
    session: AsyncSession = Depends(get_session, use_cache=True),
    current_user: Optional[User] = Depends(get_user_or_none),
):
    """Поиск издательств по названию."""
    return await get_publishers(session, search=name, user_id=current_user.id if current_user else None)


@router.get("/authors", response_model=list[str])
async def get_authors_view(
    name: str | None = Query(None, description="Авторы книги"),
    session: AsyncSession = Depends(get_session, use_cache=True),
    current_user: Optional[User] = Depends(get_user_or_none),
):
    """Поиск авторов по названию."""
    return await get_authors(session, search=name, user_id=current_user.id if current_user else None)


@router.get("/last-viewed", response_model=BooksWithReadPagesPaginatedSchema)
async def get_last_viewed_books_view(
    paginator: dict = Depends(paginator_query),
    session: AsyncSession = Depends(get_session, use_cache=True),
    user: User = Depends(get_current_user),
):
    """Возвращает просмотренные книги пользователя с кол-вом просмотренных страниц."""
    return await get_last_viewed_books(session, user.id, paginator)


def books_query_params(
    search: str | None = Query(None, max_length=254, description="Поиск по названию и описанию"),
    title: str | None = Query(None, max_length=254, description="Заголовок"),
    authors: str | None = Query(None, max_length=254, description="Авторы книги"),
    publisher: str | None = Query(None, max_length=128, description="Издательство"),
    year: int | None = Query(None, gt=0, description="Год издания"),
    language: str | None = Query(None, max_length=128, description="Язык книги"),
    pages_gt: int | None = Query(None, gt=0, alias="pages-gt", description="Количество страниц больше чем"),
    pages_lt: int | None = Query(None, gt=0, alias="pages-lt", description="Количество страниц меньше чем"),
    description: str | None = Query(None, description="Описание книги"),
    only_private: bool | None = Query(False, alias="only-private", description="Только приватные книги"),
    tags: list[str] | None = Query([], description="Теги книги"),
    page: int = Query(1, gt=0, description="Номер страницы"),
    per_page: int = Query(25, gte=1, alias="per-page", description="Количество элементов на странице"),
) -> QueryParams:
    """Параметры поиска по книгам."""

    if pages_gt and pages_lt and pages_gt >= pages_lt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="pages_gt must be less than pages_lt",
        )
    return {
        "search": search,
        "title": title,
        "authors": authors,
        "publisher": publisher,
        "year": year,
        "language": language,
        "pages_gt": pages_gt,
        "pages_lt": pages_lt,
        "description": description,
        "only_private": only_private,
        "tags": tags,
        "page": page,
        "per_page": per_page,
    }


@router.get("", response_model=BooksSchemaPaginated)
async def get_books_view(
    query_params: QueryParams = Depends(books_query_params),
    current_user: Optional[User] = Depends(get_user_or_none),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Просмотр всех книг с фильтрацией по запросу."""
    return await get_filtered_books(session, current_user.id if current_user else None, query_params)


@router.post("", response_model=BookSchemaWithDesc, status_code=status.HTTP_201_CREATED)
async def create_book_view(
    book_data: CreateBookSchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Создание книги"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для создания книги"
        )
    book = await create_book(session, current_user, book_data)
    # Удаляем кэш недавно добавленных книг, потому что добавилась новая книга.
    await delete_recent_books_cache()
    return book


@router.get("/{book_id}", response_model=BookSchemaDetail)
async def get_book_view(
    book_id: int,
    current_user: Optional[User] = Depends(get_user_or_none),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Просмотр книги"""
    book_schema = await get_book_detail(session, book_id, current_user.id if current_user else None)
    return book_schema


@router.put("/{book_id}", response_model=BookSchemaWithDesc)
async def update_book_view(
    book_id: int,
    book_data: CreateBookSchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Обновление книги"""
    book = await get_book(session, book_id)
    await check_book_owner_permission(session, current_user.id, book)
    book = await update_book(session, book, book_data)
    # Удаляем кэш недавно добавленных книг, потому что могло поменять название книги
    await delete_recent_books_cache()
    return BookSchemaWithDesc.model_validate(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_view(
    book_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Удаление книги"""
    await check_book_owner_permission(session, current_user.id, book_id)
    await delete_book(session, book_id)
    # Удаляем кэш недавно добавленных книг, потому что могла удалиться новая книга
    await delete_recent_books_cache()


@router.post("/{book_id}/upload", response_model=BookSchema)
async def upload_book_file(
    book_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Загрузка файла книги"""
    if file.filename is None or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Формат файла должен быть только '.pdf'"
        )

    book = await get_book(session, book_id)
    await check_book_owner_permission(session, current_user.id, book)

    await set_file(session, file, book)
    create_book_preview_task.delay(book.id)  # Отправляем задачу

    return BookSchema.model_validate(book)


@router.get("/{book_id}/download", response_class=StreamingResponse)
async def download_book_file(
    book_id: int,
    user: Optional[User] = Depends(get_user_or_none),
    as_file: bool = Query(False, alias="as-file"),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Скачивание файла книги"""
    book = await get_book(session, book_id)
    if book.private and (user is None or book.user_id != user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на скачивание файла данной книги",
        )
    storage = get_storage()

    headers = {
        "Cache-Control": "max-age=86400",
    }
    if as_file:
        headers["Content-Disposition"] = f'attachment; filename="{slugify(book.title)}.pdf"'

    try:
        book_async_iterator = storage.get_book_iterator(book.id)
    except storage.FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл книги не найден")

    return StreamingResponse(
        content=book_async_iterator,
        media_type="application/pdf",
        headers=headers,
    )
