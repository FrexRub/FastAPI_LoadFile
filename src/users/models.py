from datetime import datetime
from uuid import uuid4
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, func, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

# if TYPE_CHECKING:
#     from src.payments.models import Score, Payment


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
    )
    full_name: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    registered_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow(),
    )
    hashed_password: Mapped[str]
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
