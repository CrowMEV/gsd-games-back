import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.db import Base


class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(length=30), unique=True)
    description: Mapped[str]
    rule_description: Mapped[str]
    price: Mapped[int]
    image: Mapped[str]
