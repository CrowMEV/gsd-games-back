import enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class RoleChoice(enum.Enum):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(length=50), default="")
    phone: Mapped[str] = mapped_column(sa.String(12), unique=True)
    avatar: Mapped[str] = mapped_column(default="")
    role: Mapped[RoleChoice] = mapped_column(
        default=RoleChoice.USER, server_default=RoleChoice.USER.name
    )
    is_active: Mapped[bool] = mapped_column(server_default=sa.true())
