from typing import Optional

from fastapi import APIRouter, UploadFile, HTTPException, Depends
from fastapi import status
from sqlalchemy.exc import NoResultFound

from ..crud.books import create_book, get_non_private_books, get_books_with_user_private
from ..models import Book, User
from ..schemas.books import BookSchema, CreateBookSchema
from ..services.auth import get_current_user, get_user_or_none
from ..services.books import set_file

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
    book = await Book.get(id=book_id)
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
