from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str]
    name: Mapped[str] = mapped_column(sa.String(length=50))
    email: Mapped[str] = mapped_column(
        sa.String(length=50), unique=True, index=True
    )
    avatar: Mapped[str] = mapped_column(default="")
    birth_date: Mapped[datetime] = mapped_column(nullable=True)
