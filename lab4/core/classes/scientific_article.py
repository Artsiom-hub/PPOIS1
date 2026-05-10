from dataclasses import dataclass, field
from typing import List


@dataclass
class ScientificArticle:
    id: int
    title: str
    authors: List[str]
    abstract: str
    status: str = "submitted"

    def change_status(self, new_status: str) -> None:
        self.status = new_status