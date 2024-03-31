from unittest import IsolatedAsyncioTestCase

from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database.connector import db_conn
from app.handlers.books import router
from app.models import Publisher, User, Tag, Book
from app.schemas.books import BookSchema
from app.services.auth import create_jwt_token_pair
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
            await conn.commit()

    @staticmethod
    async def create_book(user: User, title: str, private: bool) -> Book:
        async with db_conn.session as conn:
            publisher = Publisher(name="Publisher")
            tags = [Tag(name="Python"), Tag(name="Django")]

            book = Book(
                user_id=user.id,
                publisher=publisher,
                title=title,
                preview_image="",
                authors="Автор-1, Автор-2",
                description="Описание",
                pages=321,
                size=1024 * 1024 * 3,
                year=2023,
                private=private,
                tags=tags,
            )

            conn.add(publisher)
            conn.add_all(tags)
            conn.add(book)
            await conn.commit()
            await conn.refresh(book)
        return book

    @staticmethod
    async def create_user(username: str) -> User:
        async with db_conn.session as conn:
            user = User(username=username, email=f"{username}@mail.com", password="<PASSWORD>")
            conn.add(user)
            await conn.commit()
            await conn.refresh(user)
            return user


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
