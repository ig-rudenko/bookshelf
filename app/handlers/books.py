from sqlalchemy.exc import NoResultFound
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from ..models import Book, User
from ..crud.books import create_book
from ..schemas.books import BookSchema, CreateBookSchema
from ..services.auth import get_current_user
from ..services.books import set_file, get_book_schema

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookSchema)
async def create_book_view(book_data: CreateBookSchema, current_user: User = Depends(get_current_user)):
    book = await create_book(current_user, book_data)
    return book


@router.post("/{book_id}/upload", response_model=BookSchema)
async def upload_book_file(book_id: int, file: UploadFile, user: User = Depends(get_current_user)):
    try:
        book = await Book.get(id=book_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this book")

    await set_file(file, book)

    return await get_book_schema(book_id)
