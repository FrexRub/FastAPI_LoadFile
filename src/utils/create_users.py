import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.engine import Result

from src.core.database import async_session_maker
from src.users.models import User
from src.files.models import File
from src.users.crud import create_user
from src.users.schemas import UserCreateSchemas
from src.core.config import configure_logging

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def create_new_users() -> None:
    """
    Утилита по созданию новых пользователей
    """
    logger.info("Start create default users")
    async with async_session_maker() as session:
        stmt = select(User).filter(User.email == "admin@mycomp.com")
        res: Result = await session.execute(stmt)
        user: User = res.scalar_one_or_none()
        if user is None:
            logger.info("Users creation completed")
            user_admin: UserCreateSchemas = UserCreateSchemas(
                full_name="Петров Иван", email="admin@mycomp.com", password="1qaz!QAZ"
            )
            admin: User = await create_user(session=session, user_data=user_admin)
            admin.is_superuser = True
            await session.commit()

            user: UserCreateSchemas = UserCreateSchemas(
                full_name="Ветлицкий Сергей",
                email="user1@mycomp.com",
                password="2wsx@WSX",
            )
            res: User = await create_user(session=session, user_data=user)
            logger.info("Users have already been created")
        else:
            logger.info("Users have already been created")


if __name__ == "__main__":
    asyncio.run(create_new_users())
