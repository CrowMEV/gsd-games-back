import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(length=30), unique=True)
    description: Mapped[str]
    rules: Mapped[str]
    image: Mapped[str]
    min_people: Mapped[int]
    max_people: Mapped[int]
    is_active: Mapped[bool] = mapped_column(server_default=sa.true())
