import os
import tempfile
from contextlib import contextmanager
from typing import AsyncIterable, BinaryIO, Generator

import aioboto3
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from .base import AbstractStorage


class S3Storage(AbstractStorage):
    def __init__(self, bucket_name: str, endpoint_url: str | None = None):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url or None
        self._s3_async = aioboto3.Session()
        self._s3_sync = boto3.client("s3", endpoint_url=endpoint_url)

    @staticmethod
    def _book_prefix(book_id: int) -> str:
        return f"books/{book_id}/"

    @staticmethod
    def _book_key(book_id: int, file_name: str) -> str:
        return f"books/{book_id}/{file_name}"

    @staticmethod
    def _file_key(file_name: str) -> str:
        return file_name

    async def upload_book(self, file: UploadFile, book_id: int) -> str:
        await self.delete_book(book_id)
        key = self._book_key(book_id, file.filename)
        async with self._s3_async.client("s3", endpoint_url=self.endpoint_url) as s3:
            await s3.upload_fileobj(file.file, self.bucket_name, key)
        return key

    def get_book_iterator(self, book_id: int) -> AsyncIterable[bytes]:
        return self._get_file_async_iterator(book_id)

    async def _get_file_async_iterator(self, book_id: int) -> AsyncIterable[bytes]:
        chunk_size = 1024 * 1024  # 1MB
        async with self._s3_async.client("s3", endpoint_url=self.endpoint_url) as s3:
            prefix = self._book_prefix(book_id)
            objects = await s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            contents = objects.get("Contents")
            if not contents:
                raise self.FileNotFoundError(f"No book found for ID {book_id}")

            key = contents[0]["Key"]
            response = await s3.get_object(Bucket=self.bucket_name, Key=key)
            stream = response["Body"]

            while True:
                chunk = await stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    @contextmanager
    def get_book_binary(self, book_id: int) -> Generator[BinaryIO, None, None]:
        prefix = self._book_prefix(book_id)
        try:
            result = self._s3_sync.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            contents = result.get("Contents")
            if not contents:
                raise self.FileNotFoundError(f"No book found for ID {book_id}")
            key = contents[0]["Key"]
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                self._s3_sync.download_fileobj(self.bucket_name, key, tmp)
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                yield f
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise self.FileNotFoundError(f"File not found for book ID {book_id}")
            raise
        finally:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

    async def upload_file(self, file_name: str, data: bytes) -> str:
        key = self._file_key(file_name)
        async with self._s3_async.client("s3", endpoint_url=self.endpoint_url) as s3:
            await s3.put_object(Bucket=self.bucket_name, Key=key, Body=data)
        return key

    @contextmanager
    def get_file_binary(self, file_name: str) -> Generator[BinaryIO, None, None]:
        key = self._file_key(file_name)
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                self._s3_sync.download_fileobj(self.bucket_name, key, tmp)
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                yield f
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise self.FileNotFoundError(f"File '{file_name}' not found")
            raise
        finally:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

    async def delete_book(self, book_id: int) -> None:
        prefix = self._book_prefix(book_id)
        async with self._s3_async.client("s3", endpoint_url=self.endpoint_url) as s3:
            response = await s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            contents = response.get("Contents")
            if contents:
                for obj in contents:
                    await s3.delete_object(Bucket=self.bucket_name, Key=obj["Key"])
