import io
from contextlib import asynccontextmanager
from typing import BinaryIO, AsyncIterable, AsyncGenerator

import aiohttp
import yadisk
from fastapi import UploadFile
from yadisk.exceptions import YaDiskError, DirectoryExistsError

from .base import AbstractStorage
from ..services.deco import singleton


@singleton
class YandexStorage(AbstractStorage):
    def __init__(self, token: str) -> None:
        self._client = yadisk.AsyncClient(token=token)
        self._media_root = "bookshelf"

    @property
    def client(self):
        return self._client

    async def mkdir(self, path: str, file_path: bool = False) -> None:
        if not await self._client.exists(path):
            parts = path.split("/")
            for i in range(1, len(parts) - int(file_path)):
                print("/".join(parts[: i + 1]))
                try:
                    await self._client.mkdir("/".join(parts[: i + 1]))
                except DirectoryExistsError:
                    pass

    async def upload_book(self, file: UploadFile, book_id: int) -> str:
        file_name = f"/{self._media_root}/books/{book_id}/{file.filename}"
        await self.mkdir(file_name, True)
        try:
            await self._client.remove(file_name)
        except YaDiskError:
            pass
        await self._client.upload(file.file, file_name)
        return file_name

    async def get_book_iterator(self, book_id: int) -> AsyncIterable[bytes]:
        link = ""
        try:
            async for book_file in await self._client.listdir(f"/{self._media_root}/books/{book_id}/"):
                link = await book_file.get_download_link()
                break
        except YaDiskError:
            raise self.FileNotFoundError
        if not link:
            raise self.FileNotFoundError

        async with aiohttp.client.ClientSession() as session:
            async with session.get(link) as response:
                async for data in response.content.iter_chunked(1024 * 1024):
                    yield data

    @asynccontextmanager
    async def get_book_binary(self, book_id: int) -> AsyncGenerator[BinaryIO, None]:
        link = ""
        try:
            async for book_file in await self._client.listdir(f"/{self._media_root}/books/{book_id}/"):
                link = await book_file.get_download_link()
                break
        except YaDiskError:
            raise self.FileNotFoundError
        if not link:
            raise self.FileNotFoundError
        file_data = io.BytesIO()
        async with aiohttp.client.ClientSession() as session:
            async with session.get(link) as response:
                file_data.write(await response.read())
        file_data.seek(0)
        yield file_data

    async def upload_file(self, file_name: str, data: bytes) -> str:
        path = f"/{self._media_root}/{file_name}"
        await self._client.remove(path)
        await self.mkdir(path, True)
        await self._client.upload(io.BytesIO(data), path)
        return path

    @asynccontextmanager
    async def get_file_binary(self, file_name: str) -> AsyncGenerator[BinaryIO, None]:
        file_link = await self._client.get_upload_link(f"/{self._media_root}/{file_name}")
        file_data = io.BytesIO()
        async with aiohttp.client.ClientSession() as session:
            async with session.get(file_link) as response:
                file_data.write(await response.read())
        yield file_data

    async def delete_book(self, book_id: int) -> None:
        await self._client.remove(f"/{self._media_root}/books/{book_id}")
        await self._client.remove(f"/{self._media_root}/previews/{book_id}")
