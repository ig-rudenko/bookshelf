import pathlib
from typing import Optional, Generator

from fastapi import APIRouter, UploadFile, HTTPException, Depends, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.books import create_book, get_filtered_books_list, update_book
from ..models import Book, User
from ..orm.session_manager import get_session
from ..schemas.books import BookSchema, CreateBookSchema, BooksListSchema
from ..services.auth import get_current_user, get_user_or_none
from ..services.books import set_file
from ..settings import settings

router = APIRouter(prefix="/books", tags=["books"])


def books_query_params(
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
    page: int | None = Query(1, gt=0, description="Номер страницы"),
    per_page: int = Query(25, gte=1, alias="per-page", description="Количество элементов на странице"),
) -> dict:
    if pages_gt and pages_lt and pages_gt >= pages_lt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="pages_gt must be less than pages_lt",
        )
    return {
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


@router.get("", response_model=BooksListSchema)
async def get_books_view(
    query_params: dict = Depends(books_query_params),
    current_user: Optional[User] = Depends(get_user_or_none),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Просмотр всех книг"""
    books, total_count = await get_filtered_books_list(session, current_user, query_params)
    books = [BookSchema.model_validate(book) for book in books]

    return BooksListSchema(
        books=books,
        total_count=total_count,
        current_page=query_params["page"],
        max_pages=total_count // query_params["per_page"] or 1,
        per_page=query_params["per_page"],
    )


@router.post("", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book_view(
    book_data: CreateBookSchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Создание книги"""
    book = await create_book(session, current_user, book_data)
    return book


@router.get("/{book_id}", response_model=BookSchema)
async def get_book_view(
    book_id: int,
    current_user: Optional[User] = Depends(get_user_or_none),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Просмотр книги"""
    try:
        book = await Book.get(session, id=book_id)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

    book_schema = BookSchema.model_validate(book)

    if not book_schema.private or (
        book_schema.private and current_user is not None and current_user.id == book_schema.user_id
    ):
        return book_schema
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на просмотр данной книги",
        )


@router.put("/{book_id}", response_model=BookSchema)
async def update_book_view(
    book_id: int,
    book_data: CreateBookSchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Обновление книги"""
    book = await Book.get(session, id=book_id)
    if book.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на обновление данной книги",
        )
    book = await update_book(session, book, book_data)
    return BookSchema.model_validate(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_view(
    book_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Удаление книги"""
    book = await Book.get(session, id=book_id)
    if book.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на удаление данной книги",
        )
    await book.delete(session)


@router.post("/{book_id}/upload", response_model=BookSchema)
async def upload_book_file(
    book_id: int,
    file: UploadFile,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Загрузка файла книги"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Формат файла должен быть только '.pdf'"
        )
    try:
        book = await Book.get(session, id=book_id)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на загрузку файла данной книги",
        )

    await set_file(session, file, book)

    return BookSchema.model_validate(book)


@router.get("/{book_id}/show", response_class=StreamingResponse)
async def download_book_file(
    book_id: int,
    user: Optional[User] = Depends(get_user_or_none),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Скачивание файла книги"""
    try:
        book = await Book.get(session, id=book_id)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")
    if book.private and book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на скачивание файла данной книги",
        )

    def get_data_from_file(file_path: pathlib.Path) -> Generator:
        with file_path.open("rb") as file:
            yield file.read()

    return StreamingResponse(
        content=get_data_from_file(settings.MEDIA_ROOT / book.file),
        media_type="application/pdf",
    )
