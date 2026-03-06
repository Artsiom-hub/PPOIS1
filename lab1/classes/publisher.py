from dataclasses import dataclass, field
from typing import List


@dataclass
class PublishingHouse:
    name: str
    journals: List[int] = field(default_factory=list)

    def add_journal(self, journal_id: int) -> None:
        self.journals.append(journal_id)