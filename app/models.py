from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, Text, CheckConstraint, Boolean
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.expression import false, true
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class User(Base):
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


class Publisher(Base):
    __tablename__ = "publishers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publishers.id", ondelete="CASCADE"))
    preview_image: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(254))
    authors: Mapped[str] = mapped_column(String(254))
    description: Mapped[str] = mapped_column(Text())
    pages: Mapped[int] = mapped_column(Integer())
    year: Mapped[int] = mapped_column(Integer())
    private: Mapped[bool] = mapped_column(Boolean)

    # Define a check constraint
    __table_args__ = (
        CheckConstraint(year > 1, name="check_year_positive"),
        CheckConstraint(pages > 0, name="check_pages_positive"),
    )
