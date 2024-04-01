import pathlib
import shutil
from unittest import IsolatedAsyncioTestCase

from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.crud.books import create_book
from app.database.connector import db_conn
from app.handlers.books import router
from app.models import Publisher, User, Tag, Book, book_tag_association
from app.schemas.books import BookSchema, CreateBookSchema
from app.services.auth import create_jwt_token_pair
from app.settings import Settings
from tests.init import TEST_DB_URL


class BaseBookTest(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        db_conn.initialize(TEST_DB_URL)
        cls.client = TestClient(router)

    async def asyncSetUp(self):
        await self.asyncTearDown()
        self.user_1 = await self.create_user("user_1")
        self.user_2 = await self.create_user("user_2")
        self.book_1 = await self.create_book(self.user_1, "book_1", private=False)
        self.book_private = await self.create_book(self.user_2, "book_2", private=True)

    async def asyncTearDown(self):
        async with db_conn.session as conn:
            await conn.execute(delete(Publisher))
            await conn.execute(delete(User))
            await conn.execute(delete(Tag))
            await conn.execute(delete(Book))
            await conn.execute(delete(book_tag_association))
            await conn.commit()

    @staticmethod
    async def create_book(user: User, title: str, private: bool) -> Book:
        book_schema = CreateBookSchema(
            publisher=f"Publisher-{user.username}",
            title=title,
            authors="Автор-1, Автор-2",
            description="Описание",
            year=2023,
            private=private,
            language="русский",
            tags=["tag_1", "tag_2"],
        )
        return await create_book(user, book_schema)

    @staticmethod
    async def create_user(username: str) -> User:
        async with db_conn.session as conn:
            user = User(username=username, email=f"{username}@mail.com", password="<PASSWORD>")
            conn.add(user)
            await conn.commit()
            await conn.refresh(user)
            return user


class CreateBookTest(BaseBookTest):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.book_valid_data = {
            "title": "book_3",
            "authors": "Автор-1, Автор-2",
            "publisher": "Publisher",
            "description": "Описание",
            "year": 2023,
            "private": True,
            "language": "русский",
            "tags": ["python", "django"],
        }
        self.book_data_no_publisher = {
            "title": "book_3",
            "authors": "Автор-1, Автор-2",
            "description": "Описание",
            "year": 2023,
            "private": True,
            "language": "русский",
            "tags": ["python", "django"],
        }
        self.book_data_no_tags = {
            "title": "book_3",
            "authors": "Автор-1, Автор-2",
            "publisher": "Publisher",
            "description": "Описание",
            "year": 2023,
            "private": True,
            "language": "русский",
        }

    async def test_create_book(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)

        response = self.client.post(
            "/books",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json=self.book_valid_data,
        )

        self.assertEqual(response.status_code, 201)
        new_book = await Book.get(title="book_3")
        valid_response = BookSchema.model_validate(new_book).model_dump()
        self.assertEqual(valid_response, response.json())

    async def test_create_book_without_auth(self):
        with self.assertRaises(HTTPException):
            self.client.post("/books", json=self.book_valid_data)

    async def test_create_book_invalid_data(self):
        with self.assertRaises(HTTPException):
            self.client.post("/books", json=self.book_data_no_publisher)
        with self.assertRaises(HTTPException):
            self.client.post("/books", json=self.book_data_no_tags)


class ListBooksTest(BaseBookTest):

    async def test_list_books(self):
        response = self.client.get("/books")
        self.assertEqual(response.status_code, 200)

        book_schema = BookSchema.model_validate(self.book_1)
        valid_data = [book_schema.model_dump()]

        self.assertEqual(valid_data, response.json())

    async def test_list_books_with_user(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)

        response = self.client.get("/books", headers={"Authorization": f"Bearer {token_pair.access_token}"})
        public_book_schema = BookSchema.model_validate(self.book_1)
        valid_data = [public_book_schema.model_dump()]

        self.assertEqual(valid_data, response.json())

    async def test_list_books_with_my_privates(self):
        token_pair = create_jwt_token_pair(user_id=self.user_2.id)

        response = self.client.get("/books", headers={"Authorization": f"Bearer {token_pair.access_token}"})
        book_schema_1 = BookSchema.model_validate(self.book_1)
        book_schema_private = BookSchema.model_validate(self.book_private)
        valid_data = [book_schema_1.model_dump(), book_schema_private.model_dump()]

        self.assertEqual(valid_data, response.json())


class BookTest(BaseBookTest):

    async def test_book_anonymous_view(self):
        response = self.client.get(f"/books/{self.book_1.id}")
        self.assertEqual(response.status_code, 200)

    async def test_book_anonymous_forbidden_view(self):
        with self.assertRaises(HTTPException):
            self.client.get(f"/books/{self.book_private.id}")

    async def test_book_non_owner_view(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException):
            self.client.get(
                f"/books/{self.book_private.id}",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
            )

    async def test_book_owner_view(self):
        token_pair = create_jwt_token_pair(user_id=self.user_2.id)
        response = self.client.get(
            f"/books/{self.book_private.id}", headers={"Authorization": f"Bearer {token_pair.access_token}"}
        )
        self.assertEqual(response.status_code, 200)


class UpdateBookTest(BaseBookTest):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.book_update_data_with_new_tag = {
            "title": "new title",
            "authors": "Автор-1, Автор-2",
            "publisher": "new Publisher",
            "description": "Описание",
            "year": 2023,
            "private": True,
            "language": "русский",
            "tags": ["mysql", "django"],
        }

    async def test_update_book_and_tags(self):
        token_pair = create_jwt_token_pair(user_id=self.user_2.id)
        before_tags_count = len(await Tag.all())
        before_publisher_count = len(await Publisher.all())

        response = self.client.put(
            f"/books/{self.book_private.id}/",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json=self.book_update_data_with_new_tag,
        )
        self.assertEqual(response.status_code, 200)

        self.book_private = await Book.get(title="new title")  # проверка изменения
        valid_response = BookSchema.model_validate(self.book_private).model_dump()
        self.assertEqual(valid_response, response.json())

        # Проверка изменения тегов
        after_tags_count = len(await Tag.all())
        self.assertEqual(after_tags_count, before_tags_count + 2)
        after_publisher_count = len(await Publisher.all())
        self.assertEqual(after_publisher_count, before_publisher_count + 1)


class UploadBookFileTest(BaseBookTest):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.file_path = pathlib.Path(__file__).parent / "sample-pdf-file.pdf"
        Settings.MEDIA_ROOT = pathlib.Path(__file__).parent / "media-test"
        Settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

    async def asyncTearDown(self):
        await super().asyncTearDown()
        if Settings.MEDIA_ROOT.name.endswith("media-test"):
            shutil.rmtree(Settings.MEDIA_ROOT, ignore_errors=True)

    async def test_upload_file(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)

        with open(self.file_path, "rb") as file:
            response = self.client.post(
                f"/books/{self.book_1.id}/upload",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
                files={"file": file},
            )

        book_media_path = Settings.MEDIA_ROOT / "books" / str(self.book_1.id)
        book_preview_path = Settings.MEDIA_ROOT / "previews" / str(self.book_1.id)

        self.assertEqual(response.status_code, 200)
        self.assertTrue((book_media_path / "sample-pdf-file.pdf").exists())
        self.assertTrue((book_preview_path / "preview.png").exists())

        self.book_1 = await Book.get(id=self.book_1.id)  # refresh book from db
        self.assertEqual(self.book_1.preview_image, f"previews/{self.book_1.id}/preview.png")
        self.assertEqual(self.book_1.file, f"books/{self.book_1.id}/sample-pdf-file.pdf")
        self.assertEqual(self.book_1.size, self.file_path.stat().st_size)

    async def test_upload_file_no_owner_user(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException):
            with open(self.file_path, "rb") as file:
                self.client.post(
                    f"/books/{self.book_private.id}/upload",
                    headers={"Authorization": f"Bearer {token_pair.access_token}"},
                    files={"file": file},
                )

    async def test_upload_file_without_auth(self):
        with self.assertRaises(HTTPException):
            with open(self.file_path, "rb") as file:
                self.client.post(f"/books/{self.book_1.id}/upload", files={"file": file})

    async def test_upload_invalid_file(self):
        with self.assertRaises(HTTPException):
            with open(__file__, "rb") as file:
                self.client.post(f"/books/{self.book_1.id}/upload", files={"file": file})

    async def test_upload_to_non_existing_book(self):
        with self.assertRaises(HTTPException):
            with open(self.file_path, "rb") as file:
                self.client.post(f"/books/0/upload", files={"file": file})
