import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Office(Base):
    __tablename__ = "offices"
    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str]
    city: Mapped[str]

    __table_args__ = (
        sa.UniqueConstraint("address", "city", name="address_city_constraint"),
    )
