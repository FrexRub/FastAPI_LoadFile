from dataclasses import dataclass
from typing import BinaryIO
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, UUID4


@dataclass(slots=True)
class FileLoadSchemas:
    file: BinaryIO
    filename: str
    new_filename: str


class FilesListSchemas(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    filename: str
    path_file: str

    model_config = ConfigDict(from_attributes=True)
