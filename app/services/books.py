import re

import fitz
from fastapi import UploadFile, status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book
from app.settings import settings


async def check_book_owner(
    session: AsyncSession, user_id: int, book_id: int | None = None, book_instance: Book | None = None
):
    """Если пользователь не является владельцем книги, выбрасывает исключение."""
    if book_instance is None and book_id is not None:
        result = await session.execute(select(Book.user_id).where(Book.id == book_id))
        book_owner_id: int | None = result.scalar_one_or_none()
    elif book_instance is not None:
        book_owner_id: int = book_instance.user_id
    else:
        raise ValueError("book_id or book_instance must be specified")

    if book_owner_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

    elif book_owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на доступ к этой книге"
        )


async def set_file(session: AsyncSession, file: UploadFile, book: Book):
    """
    Создаем для книги файл, а также превью для его просмотра.
    """
    file_name = file.filename or f"book_{book.id}.pdf"
    # Фильтруем запрещенные символы
    file_name = re.sub(r"[<>#%\"|^\[\]`;?:@&=+$ ]+", "_", file_name)
    # Создаем директорию для хранения книги
    book_folder = settings.media_root / "books" / str(book.id)
    preview_folder = settings.media_root / "previews" / str(book.id)
    book_folder.mkdir(parents=True, exist_ok=True)
    preview_folder.mkdir(parents=True, exist_ok=True)

    # Удаляем старый файл книги
    for old_file in book_folder.glob("*.pdf"):
        old_file.unlink()

    # Открытие файла в бинарном режиме.
    with (book_folder / file_name).open("wb") as upload_file:
        # Чтение файла по частям, а затем его запись.
        upload_file.write(file.file.read())  # Записываем файл

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
    book.preview_image = f"previews/{book.id}/preview.png"
    book.size = book_file_path.stat().st_size
    book.pages = doc.page_count
    await book.save(session)
