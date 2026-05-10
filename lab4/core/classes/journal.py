from dataclasses import dataclass, field
from typing import List


@dataclass
class Journal:
    id: int
    name: str
    field: str
    articles: List[int] = field(default_factory=list)

    def add_article(self, article_id: int) -> None:
        self.articles.append(article_id)