import pathlib
from typing import Optional, Generator

from fastapi import APIRouter, UploadFile, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import NoResultFound

from ..crud.books import create_book, get_non_private_books, get_books_with_user_private, update_book
from ..models import Book, User
from ..schemas.books import BookSchema, CreateBookSchema
from ..services.auth import get_current_user, get_user_or_none
from ..services.books import set_file
from ..settings import Settings

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[BookSchema])
async def get_books_view(current_user: Optional[User] = Depends(get_user_or_none)):
    """Просмотр всех книг"""
    if current_user is not None:
        books = await get_books_with_user_private(current_user.id)
    else:
        books = await get_non_private_books()
    return [BookSchema.model_validate(book) for book in books]


@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book_view(book_data: CreateBookSchema, current_user: User = Depends(get_current_user)):
    """Создание книги"""
    book = await create_book(current_user, book_data)
    return book


@router.get("/{book_id}", response_model=BookSchema)
async def get_book_view(book_id: int, current_user: Optional[User] = Depends(get_user_or_none)):
    """Просмотр книги"""
    try:
        book = await Book.get(id=book_id)
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
    book_id: int, book_data: CreateBookSchema, current_user: User = Depends(get_current_user)
):
    """Обновление книги"""
    book = await Book.get(id=book_id)
    if book.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на обновление данной книги",
        )
    book = await update_book(book, book_data)
    return BookSchema.model_validate(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_view(book_id: int, current_user: User = Depends(get_current_user)):
    """Удаление книги"""
    book = await Book.get(id=book_id)
    if book.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на удаление данной книги",
        )
    await book.delete()


@router.post("/{book_id}/upload", response_model=BookSchema)
async def upload_book_file(book_id: int, file: UploadFile, user: User = Depends(get_current_user)):
    """Загрузка файла книги"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Формат файла должен быть только '.pdf'"
        )
    try:
        book = await Book.get(id=book_id)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на загрузку файла данной книги",
        )

    await set_file(file, book)

    return BookSchema.model_validate(book)


@router.get("/{book_id}/show", response_class=StreamingResponse)
async def download_book_file(book_id: int, user: Optional[User] = Depends(get_user_or_none)):
    """Скачивание файла книги"""
    try:
        book = await Book.get(id=book_id)
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
        content=get_data_from_file(Settings.MEDIA_ROOT / book.file),
        media_type="application/pdf",
    )
