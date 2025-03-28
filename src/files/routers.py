import logging

from fastapi import APIRouter, UploadFile, HTTPException, status

from src.files.schemas import FileLoadSchemas
from src.files.utils import load_media_file
from src.core.config import configure_logging
from src.core.exceptions import ErrorInData

router = APIRouter(prefix="/files", tags=["files"])

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/load")
async def load_file(new_name_file: str, upload_file: UploadFile):
    file_load = FileLoadSchemas(
        file=upload_file.file, filename=upload_file.filename, new_filename=new_name_file
    )
    try:
        await load_media_file(loadfile=file_load)
    except ErrorInData as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    return {"response": "OK"}
