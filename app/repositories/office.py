from sqlalchemy.ext.asyncio import AsyncSession

import models
import repositories.common as common_repository


class Office(common_repository.Base[models.Office]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = models.Office
