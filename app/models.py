from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, Text, CheckConstraint, Boolean
from sqlalchemy import Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import false, true
from sqlalchemy.sql.functions import func

from app.crud.manager import Manager
from app.orm.base_model import OrmBase


class User(OrmBase, Manager):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(150))
    last_name: Mapped[Optional[str]] = mapped_column(String(150))
    email: Mapped[Optional[str]] = mapped_column(String(254), unique=True)
    password: Mapped[str] = mapped_column(String(128))
    last_login: Mapped[Optional[datetime]] = mapped_column()
    is_superuser: Mapped[bool] = mapped_column(server_default=false())
    is_staff: Mapped[bool] = mapped_column(server_default=false())
    is_active: Mapped[bool] = mapped_column(server_default=true())
    date_join: Mapped[datetime] = mapped_column(server_default=func.now())
    favorites = relationship(
        "Book", secondary="favorite_books", back_populates="favorite_for_users", lazy="select"
    )
    books_read = relationship("Book", secondary="books_read", back_populates="read_by_users", lazy="select")
    comments = relationship("Comment", back_populates="user", lazy="select")

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<User {self.username}>"


class Publisher(OrmBase, Manager):
    __tablename__ = "publishers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    books: Mapped["Book"] = relationship("Book", back_populates="publisher", lazy="select")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Publisher: {self.name}>"


# Define association table for many-to-many relationship between Tag and Book
book_tag_association = Table(
    "book_tag_association",
    OrmBase.metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
)


class Tag(OrmBase, Manager):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    # Define relationship to Book using the association table
    books = relationship("Book", secondary=book_tag_association, back_populates="tags", lazy="select")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Tag: {self.name}>"


class Book(OrmBase, Manager):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publishers.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String(254))
    preview_image: Mapped[str] = mapped_column(String(128))
    file: Mapped[str] = mapped_column(String(128))
    authors: Mapped[str] = mapped_column(String(254))
    description: Mapped[str] = mapped_column(Text)
    pages: Mapped[int] = mapped_column(Integer())
    size: Mapped[int] = mapped_column(Integer())
    year: Mapped[int] = mapped_column(Integer())
    private: Mapped[bool] = mapped_column(Boolean)
    language: Mapped[str] = mapped_column(String(128))

    # Define relationship to Tag using the association table
    tags = relationship("Tag", secondary=book_tag_association, back_populates="books", lazy="joined")
    # Define relationship to Publisher, User
    publisher: Mapped[Publisher] = relationship("Publisher", back_populates="books", lazy="joined")
    user: Mapped[User] = relationship("User")
    favorite_for_users = relationship(
        "User", secondary="favorite_books", back_populates="favorites", lazy="select"
    )
    read_by_users = relationship("User", secondary="books_read", back_populates="books_read", lazy="select")
    comments = relationship("Comment", back_populates="book", cascade="all, delete-orphan", lazy="select")

    # Define a check constraint
    __table_args__ = (
        CheckConstraint(year > 1, name="check_year_positive"),
        CheckConstraint(pages > 0, name="check_pages_positive"),
    )

    def __repr__(self):
        return f"<Book: {self.title}>"


class Comment(OrmBase, Manager):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user: Mapped[User] = relationship("User", back_populates="comments", lazy="select")
    book: Mapped[Book] = relationship("Book", back_populates="comments", lazy="select")

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"<Comment: {self.text}>"


# Избранные книги
favorite_books_association = Table(
    "favorite_books",
    OrmBase.metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE")),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
)


# Уже прочитанные книги
books_read_association = Table(
    "books_read",
    OrmBase.metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE")),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
)
