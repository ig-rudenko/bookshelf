from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, favorite_books_association, books_read_association
from app.schemas.users import UserSchemaPaginated, UserDetailSchema
from app.services.paginator import paginate


async def get_all_users(session: AsyncSession, paginator) -> UserSchemaPaginated:
    query = (
        select(
            User.id,
            User.username,
            User.email,
            User.first_name,
            User.last_name,
            User.is_superuser,
            User.is_staff,
            User.date_join,
            func.count(func.distinct(favorite_books_association.c.book_id)).label("favorite_books_count"),
            func.count(func.distinct(books_read_association.c.book_id)).label("books_read_count"),
        )
        .outerjoin(favorite_books_association, User.id == favorite_books_association.c.user_id)
        .outerjoin(books_read_association, User.id == books_read_association.c.user_id)
        .group_by(User.id)
    )
    query = paginate(query, page=paginator["page"], per_page=paginator["per_page"])
    result = await session.execute(query)
    all_users_count = (await session.execute(select(func.count(User.id)).select_from(User))).scalar_one()

    users = [
        UserDetailSchema(
            id=row[0],
            username=row[1],
            email=row[2],
            first_name=row[3],
            last_name=row[4],
            is_superuser=row[5],
            is_staff=row[6],
            date_join=row[7],
            favorites_count=row[8],
            read_count=row[9],
        )
        for row in result
    ]
    return UserSchemaPaginated(
        results=users,
        total_count=all_users_count,
        current_page=paginator["page"],
        max_pages=all_users_count // paginator["per_page"] or 1,
        per_page=paginator["per_page"],
    )
