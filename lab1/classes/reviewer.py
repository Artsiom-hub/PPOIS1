from dataclasses import dataclass


@dataclass
class Editor:
    id: int
    name: str
    field: str

    def review_article(self, article_id: int) -> str:
        return f"Editor {self.name} reviewed article {article_id}"