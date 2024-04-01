import re

import fitz
from fastapi import UploadFile, status
from fastapi.exceptions import HTTPException

from app.models import Book
from app.settings import Settings


async def set_file(file: UploadFile, book: Book):
    """
    Создаем для книги файл, а также превью для его просмотра.
    """

    # Фильтруем запрещенные символы
    file_name = re.sub(r"[<>#%\"|^\[\]`;?:@&=+$ ]+", "_", file.filename)
    # Создаем директорию для хранения книги
    book_folder = Settings.MEDIA_ROOT / "books" / str(book.id)
    preview_folder = Settings.MEDIA_ROOT / "previews" / str(book.id)
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
    await book.save()
