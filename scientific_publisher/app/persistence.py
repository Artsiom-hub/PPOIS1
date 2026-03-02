import json
from pathlib import Path
from typing import Any
from app.models import Manuscript, Review
from app.enums import ManuscriptStatus, ReviewStatus


DATA_FILE = Path("data/storage.json")


def save(repo_data: list[Manuscript]) -> None:
    DATA_FILE.parent.mkdir(exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump([_serialize(m) for m in repo_data], f, indent=4)


def load() -> list[Manuscript]:
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return [_deserialize(item) for item in raw]


def _serialize(m: Manuscript) -> dict[str, Any]:
    return {
        "id": m.id,
        "title": m.title,
        "authors": m.authors,
        "status": m.status.value,
        "reviews": [
            {
                "reviewer": r.reviewer,
                "recommendation": r.recommendation,
                "status": r.status.value,
            }
            for r in m.reviews
        ],
    }


def _deserialize(data: dict[str, Any]) -> Manuscript:
    manuscript = Manuscript(
        title=data["title"],
        authors=data["authors"],
        id=data["id"],
        status=ManuscriptStatus(data["status"]),
    )
    manuscript.reviews = [
        Review(
            reviewer=r["reviewer"],
            recommendation=r["recommendation"],
            status=ReviewStatus(r["status"]),
        )
        for r in data["reviews"]
    ]
    return manuscript