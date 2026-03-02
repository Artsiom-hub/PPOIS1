from typing import Dict
from app.models import Manuscript
from app.exceptions import EntityNotFound


class ManuscriptRepository:

    def __init__(self) -> None:
        self._storage: Dict[str, Manuscript] = {}

    def add(self, manuscript: Manuscript) -> None:
        self._storage[manuscript.id] = manuscript

    def get(self, manuscript_id: str) -> Manuscript:
        if manuscript_id not in self._storage:
            raise EntityNotFound("Manuscript not found")
        return self._storage[manuscript_id]

    def list_all(self) -> list[Manuscript]:
        return list(self._storage.values())