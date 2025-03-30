from datetime import datetime
from uuid import uuid4
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    func,
    UUID,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.users.models import User


class File(Base):
    __tablename__ = "files"
    __table_args__ = (
        UniqueConstraint("filename", "user_id", name="idx_unique_filename_user"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
    )
    filename: Mapped[str]
    path_file: Mapped[str]
    registered_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="files")
