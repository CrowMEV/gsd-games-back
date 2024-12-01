import enum
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Date

from models.base import Base


class RoleChoice(enum.Enum):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(length=50))
    password: Mapped[str]
    email: Mapped[str] = mapped_column(
        sa.String(length=50), unique=True, index=True
    )
    phone: Mapped[str] = mapped_column(sa.String(10), default="")
    avatar: Mapped[str] = mapped_column(default="")
    # pylint: disable=C0301
    birth_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)  # type: ignore[valid-type]
    role: Mapped[RoleChoice] = mapped_column(
        default=RoleChoice.USER, server_default=RoleChoice.USER.name
    )
    is_active: Mapped[bool] = mapped_column(server_default=sa.true())
