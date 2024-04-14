import re

import aiofiles
import fitz
from fastapi import UploadFile, status
from fastapi.exceptions import HTTPException
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book
from app.settings import settings


async def set_file(session: AsyncSession, file: UploadFile, book: Book):
    """
    Создаем для книги файл, а также превью для его просмотра.
    """
    # Фильтруем запрещенные символы
    file_name = re.search(r"(?P<file_name>.+)\.pdf$", file.filename).group("file_name") or f"book_{book.id}"
    file_name = slugify(file_name) + ".pdf"
    # Создаем директорию для хранения книги
    book_folder = settings.media_root / "books" / str(book.id)
    preview_folder = settings.media_root / "previews" / str(book.id)
    book_folder.mkdir(parents=True, exist_ok=True)
    preview_folder.mkdir(parents=True, exist_ok=True)

    # Удаляем старый файл книги
    for old_file in book_folder.glob("*.pdf"):
        old_file.unlink()

    async with aiofiles.open(book_folder / file_name, "wb") as f:
        while content := await file.read(1024):
            await f.write(content)

    # Получаем расширение файла
    book_file_path = book_folder / file_name
    book_preview_path = preview_folder / "preview.png"

    try:
        doc = fitz.Document(book_file_path.absolute())
    except fitz.FileDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка чтения файла, загрузите другой"
        )

    page = doc.load_page(0)
    pix = page.get_pixmap()
    pix.save(book_preview_path.absolute())

    book.file = f"books/{book.id}/{file_name}"
    book.preview_image = f"{settings.media_url}/previews/{book.id}/preview.png"
    book.size = book_file_path.stat().st_size
    book.pages = doc.page_count
    await book.save(session)
