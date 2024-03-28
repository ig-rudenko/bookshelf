from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, Text, CheckConstraint, Boolean
from sqlalchemy import Table, Column
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.expression import false, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, Manager


class User(Base, Manager):
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

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<User {self.username}>"


class Publisher(Base, Manager):
    __tablename__ = "publishers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Publisher: {self.name}>"


# Define association table for many-to-many relationship between Tag and Book
book_tag_association = Table(
    "book_tag_association",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    # Define relationship to Book using the association table
    books = relationship("Book", secondary=book_tag_association, back_populates="tags")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Tag: {self.name}>"


class Book(Base, Manager):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publishers.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String(254))
    preview_image: Mapped[str] = mapped_column(String(128))
    authors: Mapped[str] = mapped_column(String(254))
    description: Mapped[str] = mapped_column(Text)
    pages: Mapped[int] = mapped_column(Integer())
    size: Mapped[int] = mapped_column(Integer())
    year: Mapped[int] = mapped_column(Integer())
    private: Mapped[bool] = mapped_column(Boolean)
    # Define relationship to Tag using the association table
    tags = relationship("Tag", secondary=book_tag_association, back_populates="books", lazy="joined")
    # Define relationship to Publisher
    publisher: Mapped[Publisher] = relationship("Publisher", lazy="joined")

    # Define a check constraint
    __table_args__ = (
        CheckConstraint(year > 1, name="check_year_positive"),
        CheckConstraint(pages > 0, name="check_pages_positive"),
    )

    def __repr__(self):
        return f"<Book: {self.title}>"
