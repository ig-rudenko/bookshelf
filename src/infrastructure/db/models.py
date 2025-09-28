from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, Text, CheckConstraint, Boolean, DateTime
from sqlalchemy import Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import false, true
from sqlalchemy.sql.functions import func

from src.infrastructure.db.base_model import OrmBase


class UserModel(OrmBase):
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
    reset_passwd_email_datetime: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    favorites = relationship(
        "BookModel", secondary="favorite_books", back_populates="favorite_for_users", lazy="select"
    )
    books_read = relationship(
        "BookModel", secondary="books_read", back_populates="read_by_users", lazy="select"
    )
    comments = relationship("CommentModel", back_populates="user", lazy="select")
    bookshelves = relationship("BookshelfModel", back_populates="user", lazy="select")

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<UserModel {self.username}>"


class PublisherModel(OrmBase):
    __tablename__ = "publishers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    books: Mapped["BookModel"] = relationship("BookModel", back_populates="publisher", lazy="select")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<PublisherModel: {self.name}>"


# Define association table for many-to-many relationship between TagModel and BookModel
book_tag_association = Table(
    "book_tag_association",
    OrmBase.metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
)


class TagModel(OrmBase):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    # Define relationship to BookModel using the association table
    books = relationship("BookModel", secondary=book_tag_association, back_populates="tags", lazy="select")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<TagModel: {self.name}>"


class BookModel(OrmBase):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publishers.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String(254))
    preview_image: Mapped[str] = mapped_column(String(254))
    file: Mapped[str] = mapped_column(String(512))
    authors: Mapped[str] = mapped_column(String(254))
    description: Mapped[str] = mapped_column(Text)
    pages: Mapped[int] = mapped_column(Integer())
    size: Mapped[int] = mapped_column(Integer())
    year: Mapped[int] = mapped_column(Integer())
    private: Mapped[bool] = mapped_column(Boolean)
    language: Mapped[str] = mapped_column(String(128))

    # Define relationship to TagModel using the association table
    tags = relationship("TagModel", secondary=book_tag_association, back_populates="books", lazy="joined")
    bookshelves: Mapped[list["BookshelfModel"]] = relationship(
        "BookshelfModel", secondary="bookshelf_book_association", back_populates="books", lazy="select"
    )
    # Define relationship to PublisherModel, UserModel
    publisher: Mapped[PublisherModel] = relationship("PublisherModel", back_populates="books", lazy="joined")
    user: Mapped[UserModel] = relationship("UserModel")
    favorite_for_users = relationship(
        "UserModel", secondary="favorite_books", back_populates="favorites", lazy="select"
    )
    read_by_users = relationship(
        "UserModel", secondary="books_read", back_populates="books_read", lazy="select"
    )
    comments = relationship(
        "CommentModel", back_populates="book", cascade="all, delete-orphan", lazy="select"
    )

    # Define a check constraint
    __table_args__ = (
        CheckConstraint(year > 1, name="check_year_positive"),
        CheckConstraint(pages > 0, name="check_pages_positive"),
    )

    def __repr__(self):
        return f"<BookModel: {self.title}>"


class BookshelfModel(OrmBase):
    __tablename__ = "bookshelf"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    private: Mapped[bool] = mapped_column(Boolean, server_default=false())

    # relations
    user: Mapped[UserModel] = relationship("UserModel", back_populates="bookshelves", lazy="select")
    books: Mapped[list[BookModel]] = relationship(
        "BookModel", secondary="bookshelf_book_association", back_populates="bookshelves", lazy="select"
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<BookshelfModel: {self.name}>"


class BookshelfBookAssociationModel(OrmBase):
    __tablename__ = "bookshelf_book_association"
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    bookshelf_id: Mapped[int] = mapped_column(ForeignKey("bookshelf.id", ondelete="CASCADE"))


class CommentModel(OrmBase):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user: Mapped[UserModel] = relationship("UserModel", back_populates="comments", lazy="select")
    book: Mapped[BookModel] = relationship("BookModel", back_populates="comments", lazy="select")

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"<CommentModel: {self.text}>"


class FavoriteBookModel(OrmBase):
    __tablename__ = "favorite_books"
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))


class ReadBookModel(OrmBase):
    __tablename__ = "books_read"
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))


class BookHistoryModel(OrmBase):
    __tablename__ = "users_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))

    pdf_history: Mapped[str] = mapped_column(String(4096), nullable=True)
    pdf_history_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
