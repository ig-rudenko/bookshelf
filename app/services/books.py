import pathlib
import re

import fitz
from sqlalchemy import select
from fastapi import UploadFile

from app.database.connector import db_conn
from app.models import Book
from app.schemas.books import BookSchema
from app.settings import MEDIA_ROOT


async def get_book_schema(book_id: int) -> BookSchema:
    async with db_conn.session as session:
        result = await session.execute(select(Book).where(Book.id == book_id))
        return BookSchema.model_validate(result.scalars().first())


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
    # old_file = book.get_file()
    # if old_file:
    #     old_file.unlink(missing_ok=True)

    # Открытие файла в бинарном режиме.
    with (book_folder / file_name).open("wb") as upload_file:
        # Чтение файла по частям, а затем его запись.
        upload_file.write(file.file.read())  # Записываем файл

    # Получаем расширение файла
    file_format = file_name.split(".")[-1]
    book_file_path = book_folder / file_name
    book_preview_path = book_folder / "preview.png"

    if file_format == "pdf":
        # Если книга в PDF формате, то превью будет первой страницей документа
        doc = fitz.Document(book_file_path.absolute())
        page = doc.load_page(0)
        pix = page.get_pixmap()
        pix.save(book_preview_path.absolute())

        book.preview_image = f"books/{book.id}/{file_name}"
        book.size = book_file_path.stat().st_size
        book.pages = doc.page_count
        await book.save()
