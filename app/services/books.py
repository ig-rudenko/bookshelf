import pathlib
import re

import fitz
from fastapi import UploadFile, status
from fastapi.exceptions import HTTPException
from sqlalchemy import select

from app.database.connector import db_conn
from app.models import Book
from app.schemas.books import BookSchema
from app.settings import MEDIA_ROOT


async def get_book_schema(book_id: int) -> BookSchema:
    async with db_conn.session as session:
        result = await session.execute(select(Book).where(Book.id == book_id))
        result.unique()
    return BookSchema.model_validate(result.scalars().first())


async def get_non_private_books() -> list[BookSchema]:
    books = []
    async with db_conn.session as session:
        result = await session.execute(select(Book).where(Book.private.is_(False)))
        result.unique()
        for book in result.scalars():
            books.append(BookSchema.model_validate(book))
    return books


async def get_books_with_user_private(user_id: int) -> list[BookSchema]:
    books = []
    async with db_conn.session as session:
        query = select(Book).where(
            Book.private.is_(False) | (Book.private.is_(True) & Book.user_id == user_id)
        )
        print(query)
        result = await session.execute(query)
        for book in result.scalars():
            books.append(BookSchema.model_validate(book))
    return books


async def set_file(file: UploadFile, book: Book):
    """
    Создаем для книги файл, а также превью для его просмотра.
    """

    # Фильтруем запрещенные символы
    file_name = re.sub(r"[<>#%\"|^\[\]`;?:@&=+$ ]+", "_", file.filename)
    # Создаем директорию для хранения книги
    book_folder = pathlib.Path(MEDIA_ROOT / "books" / str(book.id))
    book_folder.mkdir(parents=True, exist_ok=True)

    # Удаляем старый файл книги
    for old_file in book_folder.glob("*.pdf"):
        old_file.unlink()

    # Открытие файла в бинарном режиме.
    with (book_folder / file_name).open("wb") as upload_file:
        # Чтение файла по частям, а затем его запись.
        upload_file.write(file.file.read())  # Записываем файл

    # Получаем расширение файла
    book_file_path = book_folder / file_name
    book_preview_path = book_folder / "preview.png"

    try:
        doc = fitz.Document(book_file_path.absolute())
    except fitz.FileDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка чтения файла, загрузите другой"
        )

    page = doc.load_page(0)
    pix = page.get_pixmap()
    pix.save(book_preview_path.absolute())

    book.preview_image = f"books/{book.id}/{file_name}"
    book.size = book_file_path.stat().st_size
    book.pages = doc.page_count
    await book.save()
