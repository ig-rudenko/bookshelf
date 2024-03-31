from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database.connector import db_conn
from app.handlers.books import router
from app.models import Publisher, User, Tag, Book
from app.schemas.books import BookSchema
from tests.init import TEST_DB_URL


class ListBooksTest(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        db_conn.initialize(TEST_DB_URL)
        cls.client = TestClient(router)

    async def asyncSetUp(self):
        await self.asyncTearDown()
        self.user_1 = await self.create_user("user_1")
        self.user_2 = await self.create_user("user_2")
        self.book_1 = await self.create_book(self.user_1, "book_1", private=False)
        self.book_2 = await self.create_book(self.user_2, "book_2", private=True)

    async def asyncTearDown(self):
        async with db_conn.session as conn:
            await conn.execute(delete(Publisher))
            await conn.execute(delete(User))
            await conn.execute(delete(Tag))
            await conn.execute(delete(Book))
            await conn.commit()

    @staticmethod
    async def create_book(user: User, title: str, private: bool):
        async with db_conn.session as conn:
            publisher = Publisher(name="Publisher")
            tags = [Tag(name="Python"), Tag(name="Django")]

            book = Book(
                user=user,
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
    async def create_user(username: str):
        async with db_conn.session as conn:
            user = User(username=username, email=f"{username}@mail.com", password="<PASSWORD>")
            conn.add(user)
            await conn.commit()
            await conn.refresh(user)
            return user

    async def test_list_books(self):
        response = self.client.get("/books")
        self.assertEqual(response.status_code, 200)

        book_schema = BookSchema.model_validate(self.book_1)
        valid_data = [book_schema.model_dump()]

        self.assertEqual(response.json(), valid_data)
