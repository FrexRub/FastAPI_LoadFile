from dataclasses import dataclass
from typing import BinaryIO


@dataclass(slots=True)
class FileLoadSchemas:
    file: BinaryIO
    filename: str
    new_filename: str
