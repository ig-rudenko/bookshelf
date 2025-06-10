import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import AsyncIterable, Any, Callable

import aiohttp
from fastapi import FastAPI
from starlette.responses import StreamingResponse

app = FastAPI()

API_URL = os.getenv("API_URL", "http://localhost:8000")

CACHE: dict[int | str, "MemoryCache"] = {}


@dataclass
class BookData:
    title: str
    desc: str
    preview_image: str


@dataclass
class MemoryCache:
    value: Any
    expire: datetime


def cache(key_get_func: Callable[[...], str], timeout: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            now = datetime.now()
            cache_key = key_get_func(*args, **kwargs)

            if data := CACHE.get(cache_key):
                if data.expire > now:
                    return data.value
                else:
                    CACHE.pop(cache_key)

            new_value = await func(*args, **kwargs)
            CACHE[cache_key] = MemoryCache(new_value, datetime.now() + timedelta(minutes=timeout))
            return new_value

        return wrapper

    return decorator


@cache(lambda *args: "origin_index", timeout=5)
async def get_origin_index() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as response:
            return await response.text()


@cache(lambda book_id: book_id, timeout=60 * 10)
async def get_book_data(book_id: int) -> BookData:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/v1/books/{book_id}") as response:
            data: dict = await response.json()
            return BookData(
                title=data["title"],
                desc=data["description"][:100] + "...",  # Короткое описание.
                preview_image=data["previewImage"],
            )


async def replace_meta_data(book_id: int) -> str:
    """
    <meta property="og:title" content="Bookshelf">
    <meta property="og:description" content="Книги для IT специалистов">
    <meta property="og:url" content="https://it-bookshelf.ru">
    <meta property="og:image" content="/img/bookshelf_icon.png">
    """
    book_data = await get_book_data(book_id)
    index_data = await get_origin_index()

    index_data = re.sub(
        r'<meta property="og:type" content=".+?">',
        f'<meta property="og:type" content="object">',
        index_data,
    )
    index_data = re.sub(
        r'<meta property="og:title" content=".+?">',
        f'<meta property="og:title" content="{book_data.title}">',
        index_data,
    )
    index_data = re.sub(
        r'<meta property="og:description" content=".+?">',
        f'<meta property="og:description" content="{book_data.desc}">',
        index_data,
    )
    index_data = re.sub(
        r'(<meta property="og:url" content=".+?)()(">)',
        lambda m: f"{m.group(1)}/book/{book_id}{m.group(3)}",
        index_data,
    )
    image_prefix = API_URL if not book_data.preview_image.startswith("http") else ""
    index_data = re.sub(
        r'<meta property="og:image" content=".+?">',
        f"""<meta property="og:image" content="{image_prefix}{book_data.preview_image}">
        <meta property="og:image:alt" content="{book_data.title}">""",
        index_data,
    )
    return index_data


async def to_async_gen(data: str) -> AsyncIterable[bytes]:
    for line in data.splitlines():
        yield line.encode("utf-8") + b"\n"


@app.get("{path:path}")
async def index(path: str):
    if match := re.match(r"/book/(\d+)", path):
        book_id = int(match.group(1))

        try:
            new_data = await replace_meta_data(book_id)
        except Exception as exc:
            print(exc)
        else:
            return StreamingResponse(to_async_gen(new_data), media_type="text/html")

    origin_index_data = await get_origin_index()
    return StreamingResponse(to_async_gen(origin_index_data), media_type="text/html")
