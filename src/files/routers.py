import logging

from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.files.schemas import FileLoadSchemas
from src.files.utils import load_media_file
from src.core.config import configure_logging
from src.core.exceptions import ErrorInData, UniqueViolationError
from src.users.models import User
from src.core.depends import current_user_authorization_cookie
from src.core.database import get_async_session

router = APIRouter(prefix="/files", tags=["files"])

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/load")
async def load_file(
    new_name_file: str,
    upload_file: UploadFile,
    user: User = Depends(current_user_authorization_cookie),
    session: AsyncSession = Depends(get_async_session),
):
    if new_name_file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file name is not specified",
        )
    file_load = FileLoadSchemas(
        file=upload_file.file, filename=upload_file.filename, new_filename=new_name_file
    )
    try:
        await load_media_file(
            session=session,
            user=user,
            loadfile=file_load,
        )
    except ErrorInData as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    except UniqueViolationError as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    return {"response": "OK"}
