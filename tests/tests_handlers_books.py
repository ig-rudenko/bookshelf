import pathlib
import shutil
from unittest import IsolatedAsyncioTestCase

from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.testclient import TestClient
from sqlalchemy.exc import NoResultFound

from app.handlers.books import router as books_router
from app.models import Publisher, User, Tag, Book
from app.orm.base_model import OrmBase
from app.orm.session_manager import db_manager
from app.schemas.books import BookSchema, CreateBookSchema, BookSchemaWithDesc
from app.services.aaa import create_jwt_token_pair
from app.services.books import create_book
from app.settings import settings
from tests.init import TEST_DB_URL, TEST_MEDIA_URL


# noinspection PyArgumentList
class BaseBookTest(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        db_manager.init(TEST_DB_URL)
        cls.client = TestClient(books_router)

    async def asyncSetUp(self):
        await self.asyncTearDown()
        self.user_1 = await self.create_user("user_1")
        self.user_2 = await self.create_user("user_2")
        self.book_1 = await self.create_book(self.user_1, "book_1", private=False)
        self.book_1.preview_image = TEST_MEDIA_URL
        self.book_private = await self.create_book(self.user_2, "book_2", private=True)
        self.book_private.preview_image = TEST_MEDIA_URL

    async def asyncTearDown(self):
        async with db_manager._engine.begin() as conn:
            await conn.run_sync(OrmBase.metadata.drop_all)
            await conn.run_sync(OrmBase.metadata.create_all)

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
        async with db_manager.session() as session:
            return await create_book(session, user, book_schema)

    @staticmethod
    async def create_user(username: str) -> User:
        async with db_manager.session() as conn:
            user = User(username=username, email=f"{username}@mail.com", password="<PASSWORD>")
            conn.add(user)
            await conn.commit()
            await conn.refresh(user)
            return user


# noinspection PyArgumentList
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
        # Меняем статус пользователя, чтобы он мог добавлять книги.
        async with db_manager.session() as session:
            self.user_1.is_staff = True
            await self.user_1.save(session)

        token_pair = create_jwt_token_pair(user_id=self.user_1.id)

        response = self.client.post(
            "/books",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json=self.book_valid_data,
        )

        self.assertEqual(response.status_code, 201)
        async with db_manager.session() as session:
            new_book = await Book.get(session, title="book_3")
        valid_response = BookSchemaWithDesc.model_validate(new_book).model_dump(by_alias=True)
        self.assertEqual(valid_response, response.json())

    async def test_create_book_not_staff_user(self):
        """Пользователь не является администратором."""
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)

        with self.assertRaises(HTTPException) as context:
            self.client.post(
                "/books",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
                json=self.book_valid_data,
            )
        self.assertEqual(context.exception.status_code, 403)

    async def test_create_book_with_same_publisher(self):
        """Поверка, что с уже имеющимся издателем новая книга добавится без проблем"""
        # Меняем статус пользователя, чтобы он мог добавлять книги.
        async with db_manager.session() as session:
            self.user_1.is_staff = True
            await self.user_1.save(session)

        token_pair = create_jwt_token_pair(user_id=self.user_1.id)

        self.book_valid_data["publisher"] = "Another Publisher"
        response = self.client.post(
            "/books",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json=self.book_valid_data,
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            "/books",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json=self.book_valid_data,
        )
        self.assertEqual(response.status_code, 201)

    async def test_create_book_without_auth(self):
        """Неавторизованный пользователь не может добавлять книги"""
        with self.assertRaises(HTTPException) as context:
            self.client.post("/books", json=self.book_valid_data)
        self.assertEqual(context.exception.status_code, 401)

    async def test_create_book_invalid_data(self):
        """Без издателя книгу не получится создать"""
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(RequestValidationError):
            self.client.post(
                "/books",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
                json=self.book_data_no_publisher,
            )
        with self.assertRaises(RequestValidationError):
            self.client.post(
                "/books",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
                json=self.book_data_no_tags,
            )


# noinspection PyArgumentList
class ListBooksTest(BaseBookTest):

    async def test_list_books(self):
        response = self.client.get("/books")

        self.assertEqual(response.status_code, 200)
        valid_data = {
            "books": [BookSchema.model_validate(self.book_1).model_dump(by_alias=True)],
            "currentPage": 1,
            "maxPages": 1,
            "perPage": 25,
            "totalCount": 1,
        }
        self.assertEqual(valid_data, response.json())

    async def test_list_books_with_user(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        response = self.client.get("/books", headers={"Authorization": f"Bearer {token_pair.access_token}"})

        self.assertEqual(response.status_code, 200)
        valid_data = {
            "books": [BookSchema.model_validate(self.book_1).model_dump(by_alias=True)],
            "currentPage": 1,
            "maxPages": 1,
            "perPage": 25,
            "totalCount": 1,
        }
        self.assertEqual(valid_data, response.json())

    async def test_list_books_with_my_privates(self):
        token_pair = create_jwt_token_pair(user_id=self.user_2.id)
        response = self.client.get("/books", headers={"Authorization": f"Bearer {token_pair.access_token}"})

        self.assertEqual(response.status_code, 200)
        valid_data = {
            "books": sorted(
                [
                    BookSchema.model_validate(self.book_1).model_dump(by_alias=True),
                    BookSchema.model_validate(self.book_private).model_dump(by_alias=True),
                ],
                key=lambda book: book["id"],
                reverse=True,
            ),
            "currentPage": 1,
            "maxPages": 1,
            "perPage": 25,
            "totalCount": 2,
        }
        self.maxDiff = None
        self.assertEqual(valid_data, response.json())


# noinspection PyArgumentList
class BookTest(BaseBookTest):

    async def test_book_anonymous_view(self):
        response = self.client.get(f"/books/{self.book_1.id}")
        self.assertEqual(response.status_code, 200)

    async def test_book_anonymous_forbidden_view(self):
        with self.assertRaises(HTTPException) as context:
            self.client.get(f"/books/{self.book_private.id}")
        self.assertEqual(context.exception.status_code, 404)

    async def test_book_non_owner_view(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException) as context:
            self.client.get(
                f"/books/{self.book_private.id}",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
            )
        self.assertEqual(context.exception.status_code, 404)

    async def test_book_owner_view(self):
        token_pair = create_jwt_token_pair(user_id=self.user_2.id)
        response = self.client.get(
            f"/books/{self.book_private.id}", headers={"Authorization": f"Bearer {token_pair.access_token}"}
        )
        self.assertEqual(response.status_code, 200)


# noinspection PyArgumentList
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

        async with db_manager.session() as session:

            before_tags_count = len(await Tag.all(session))
            before_publisher_count = len(await Publisher.all(session))

            response = self.client.put(
                f"/books/{self.book_private.id}/",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
                json=self.book_update_data_with_new_tag,
            )
            self.assertEqual(response.status_code, 200)

            self.book_private = await Book.get(session, title="new title")  # проверка изменения
            valid_response = BookSchemaWithDesc.model_validate(self.book_private).model_dump(by_alias=True)
            self.assertEqual(valid_response, response.json())

            # Проверка изменения тегов
            after_tags_count = len(await Tag.all(session))
            self.assertEqual(after_tags_count, before_tags_count + 2)
            after_publisher_count = len(await Publisher.all(session))
            self.assertEqual(after_publisher_count, before_publisher_count + 1)

    async def test_update_book_no_auth(self):
        with self.assertRaises(HTTPException) as context:
            self.client.put(
                f"/books/{self.book_private.id}/",
                json=self.book_update_data_with_new_tag,
            )
        self.assertEqual(context.exception.status_code, 401)

    async def test_update_book_not_owner(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException) as context:
            self.client.put(
                f"/books/{self.book_private.id}/",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
                json=self.book_update_data_with_new_tag,
            )
        self.assertEqual(context.exception.status_code, 403)

    async def test_update_invalid_book(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException) as context:
            self.client.put(
                "/books/0",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
                json=self.book_update_data_with_new_tag,
            )
        self.assertEqual(context.exception.status_code, 404)


# noinspection PyArgumentList
class DeleteBookTest(BaseBookTest):
    async def test_delete_book(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        response = self.client.delete(
            f"/books/{self.book_1.id}",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )
        self.assertEqual(response.status_code, 204)

        async with db_manager.session() as session:
            with self.assertRaises(NoResultFound):  # Книги больше нет
                await Book.get(session, title=self.book_1.title)

    async def test_delete_book_anonymous(self):
        with self.assertRaises(HTTPException) as context:
            self.client.delete(f"/books/{self.book_1.id}")
        self.assertEqual(context.exception.status_code, 401)
        async with db_manager.session() as session:
            await Book.get(session, title=self.book_1.title)

    async def test_delete_book_not_owner(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException) as context:
            self.client.delete(
                f"/books/{self.book_private.id}",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
            )
        self.assertEqual(context.exception.status_code, 403)

        async with db_manager.session() as session:
            await Book.get(session, title=self.book_private.title)

    async def test_delete_invalid_book(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException) as context:
            self.client.delete("/books/0", headers={"Authorization": f"Bearer {token_pair.access_token}"})
        self.assertEqual(context.exception.status_code, 404)


# noinspection PyArgumentList
class UploadBookFileTest(BaseBookTest):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.file_path = pathlib.Path(__file__).parent / "sample-pdf-file.pdf"

    async def asyncTearDown(self):
        await super().asyncTearDown()
        if settings.media_root.name.endswith("media-test"):
            shutil.rmtree(settings.media_root, ignore_errors=True)

    async def test_upload_file(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)

        with open(self.file_path, "rb") as file:
            response = self.client.post(
                f"/books/{self.book_1.id}/upload",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
                files={"file": file},
            )

        book_media_path = settings.media_root / "books" / str(self.book_1.id)
        book_preview_path = settings.media_root / "previews" / str(self.book_1.id)

        self.assertEqual(response.status_code, 200)
        self.assertTrue((book_media_path / "sample-pdf-file.pdf").exists())
        self.assertTrue((book_preview_path / "preview.png").exists())

        async with db_manager.session() as session:
            self.book_1 = await Book.get(session, id=self.book_1.id)  # refresh book from db

        self.assertEqual(self.book_1.preview_image, f"previews/{self.book_1.id}/preview.png")
        self.assertEqual(self.book_1.file, f"books/{self.book_1.id}/sample-pdf-file.pdf")
        self.assertEqual(self.book_1.size, self.file_path.stat().st_size)

    async def test_upload_file_no_owner_user(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException) as context:
            with open(self.file_path, "rb") as file:
                self.client.post(
                    f"/books/{self.book_private.id}/upload",
                    headers={"Authorization": f"Bearer {token_pair.access_token}"},
                    files={"file": file},
                )
        self.assertEqual(context.exception.status_code, 403)

    async def test_upload_file_without_auth(self):
        with self.assertRaises(HTTPException) as context:
            with open(self.file_path, "rb") as file:
                self.client.post(f"/books/{self.book_1.id}/upload", files={"file": file})
        self.assertEqual(context.exception.status_code, 401)

    async def test_upload_invalid_file(self):
        with self.assertRaises(HTTPException) as context:
            with open(__file__, "rb") as file:
                self.client.post(f"/books/{self.book_1.id}/upload", files={"file": file})
        self.assertEqual(context.exception.status_code, 401)

    async def test_upload_to_non_existing_book(self):
        with self.assertRaises(HTTPException) as context:
            with open(self.file_path, "rb") as file:
                self.client.post("/books/0/upload", files={"file": file})
        self.assertEqual(context.exception.status_code, 401)
