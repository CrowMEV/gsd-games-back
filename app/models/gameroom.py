from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Date

from models.base import Base


class GameRoom(Base):
    __tablename__ = "game_room"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(sa.ForeignKey("games.id"))
    office_id: Mapped[int] = mapped_column(sa.ForeignKey("offices.id"))
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    price: Mapped[int]
    image: Mapped[str]
