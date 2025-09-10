import models
import repositories.common as common_repository


class Game(common_repository.Base[models.Game]):
    def __init__(self, session):
        super().__init__(session)
        self.model = models.Game
        self.actions = {"create": self.create_item, "update": self.update_item}
