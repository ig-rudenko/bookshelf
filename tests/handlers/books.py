from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database.connector import db_conn
from app.handlers.books import router
from app.models import Publisher, User, Tag, Book
from app.schemas.books import BookSchema


class ListBooksTest(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(router)

    async def asyncSetUp(self):
        await self.asyncTearDown()
        async with db_conn.session as conn:
            user = User(username="test", email="<EMAIL>", password="<PASSWORD>")
            publisher = Publisher(name="Publisher")
            tags = [Tag(name="Python"), Tag(name="Django")]

            book = Book(
                user=user,
                publisher=publisher,
                title="Книга по Django",
                preview_image="",
                authors="Автор-1, Автор-2",
                description="Описание",
                pages=321,
                size=1024 * 1024 * 3,
                year=2023,
                private=False,
                tags=tags,
            )

            conn.add(publisher)
            conn.add(user)
            conn.add_all(tags)
            conn.add(book)
            await conn.commit()
            await conn.refresh(book)

    async def asyncTearDown(self):
        async with db_conn.session as conn:
            await conn.execute(delete(Publisher))
            await conn.execute(delete(User))
            await conn.execute(delete(Tag))
            await conn.execute(delete(Book))
            await conn.commit()

    async def test_list_books(self):
        response = self.client.get("/books")
        self.assertEqual(response.status_code, 200)

        book = await Book.get(title="Книга по Django")
        book_schema = BookSchema.model_validate(book)
        valid_data = [book_schema.model_dump()]

        self.assertEqual(response.json(), valid_data)
