import logging

import aiofiles

from src.files.schemas import FileLoadSchemas
from src.core.config import UPLOAD_DIR
from src.core.config import configure_logging
from src.core.exceptions import ErrorInData

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def load_media_file(loadfile: FileLoadSchemas):
    logger.info("Start write file by name %s", loadfile.new_filename)
    point = loadfile.filename.rfind(".")
    if point and loadfile.filename[point + 1 :].lower() in (
        "mp3",
        "aac",
        "wav",
        "flac",
        "alac",
    ):
        filename = loadfile.new_filename + loadfile.filename[point:]
        async with aiofiles.open(UPLOAD_DIR / filename, mode="wb") as f:
            await f.write(loadfile.file.read())
    else:
        logger.error("invalid format file")
        raise ErrorInData("invalid format file")
