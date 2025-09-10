import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import models
import repositories.common as common_repository


class User(common_repository.Base[models.User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = models.User

    async def get_user(self, email: str) -> models.User | None:
        return await self.session.scalar(
            sa.select(self.model).where(self.model.email == email)
        )
