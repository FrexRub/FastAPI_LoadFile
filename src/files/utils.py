import logging
from pathlib import Path
from uuid import UUID

import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError

from src.files.schemas import FileLoadSchemas
from src.core.config import UPLOAD_DIR
from src.core.config import configure_logging
from src.core.exceptions import ErrorInData, UniqueViolationError
from src.users.models import User
from src.files.models import File

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def load_media_file(
    session: AsyncSession,
    user: User,
    loadfile: FileLoadSchemas,
):
    logger.info("Start write file by name %s", loadfile.new_filename)
    point = loadfile.filename.rfind(".")
    if point and loadfile.filename[point + 1 :].lower() in (
        "mp3",
        "aac",
        "wav",
        "flac",
        "alac",
    ):
        user_email: str = user.email.lower()
        nic_name: str = user_email.replace(
            ".",
            "_",
        )
        nic_name: str = nic_name.replace(
            "@",
            "_",
        )

        filename: str = loadfile.new_filename + loadfile.filename[point:]

        folder_path: Path = Path(UPLOAD_DIR / nic_name)
        folder_path.mkdir(parents=True, exist_ok=True)
        dir_file_full: str = str(folder_path)
        dir_file: str = dir_file_full[dir_file_full.find("upload") :]

        file_user: File = File(
            filename=filename,
            path_file=dir_file,
            user=user,
        )
        try:
            session.add(file_user)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise UniqueViolationError("Duplicate name files")

        async with aiofiles.open(folder_path / filename, mode="wb") as f:
            await f.write(loadfile.file.read())
    else:
        logger.error("invalid format file")
        raise ErrorInData("invalid format file")


async def list_files(session: AsyncSession, user_id: UUID) -> list[File]:
    logger.info("Get list files for user with id: %s", user_id)

    stmt = select(File).filter(File.user_id == user_id)
    result: Result = await session.execute(stmt)
    files = result.scalars().all()

    return list(files)
