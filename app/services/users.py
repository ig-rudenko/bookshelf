from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, favorite_books_association, books_read_association, UserData
from app.schemas.users import UserSchemaPaginated, UserDetailSchema
from app.services.paginator import paginate


async def get_all_users(session: AsyncSession, query_params: dict) -> UserSchemaPaginated:
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
            func.count(func.distinct(favorite_books_association.c.book_id)).label("favorites_count"),
            func.count(func.distinct(books_read_association.c.book_id)).label("read_count"),
            func.count(func.distinct(UserData.book_id)).label("recently_read_count"),
        )
        .outerjoin(favorite_books_association, User.id == favorite_books_association.c.user_id)
        .outerjoin(books_read_association, User.id == books_read_association.c.user_id)
        .outerjoin(UserData, User.id == UserData.user_id)
        .group_by(User.id)
    )

    if sort_by := query_params.get("sort_by"):
        if sort_by == "favorites_count":
            query = query.order_by(func.count(favorite_books_association.c.book_id).desc())
        elif sort_by == "read_count":
            query = query.order_by(func.count(books_read_association.c.book_id).desc())
        elif sort_by == "recently_read_count":
            query = query.order_by(func.count(UserData.book_id).desc())
        elif hasattr(User, sort_by):
            if query_params.get("sort_order") == "desc":
                query = query.order_by(getattr(User, sort_by).desc())
            else:
                query = query.order_by(getattr(User, sort_by).asc())

    query = paginate(query, page=query_params["page"], per_page=query_params["per_page"])
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
            recently_read_count=row[10],
        )
        for row in result
    ]
    return UserSchemaPaginated(
        results=users,
        total_count=all_users_count,
        current_page=query_params["page"],
        max_pages=all_users_count // query_params["per_page"] or 1,
        per_page=query_params["per_page"],
    )
