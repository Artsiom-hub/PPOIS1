from dataclasses import dataclass
from typing import List


@dataclass
class Author:
    id: int
    name: str
    affiliation: str
    email: str

    def __str__(self) -> str:
        return f"{self.name} ({self.affiliation})"