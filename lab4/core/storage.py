import json
from pathlib import Path

from .classes.author import Author
from .classes.reviewer import Editor
from .classes.scientific_article import ScientificArticle
from .classes.journal import Journal
from .classes.publisher import PublishingHouse


LAB4_DIR = Path(__file__).resolve().parents[1]
FILE_PATH = LAB4_DIR / "data" / "state.json"


def save_state(authors, editors, articles, journals, publisher):
    data = {
        "authors": {k: vars(v) for k, v in authors.items()},
        "editors": {k: vars(v) for k, v in editors.items()},
        "articles": {k: vars(v) for k, v in articles.items()},
        "journals": {k: vars(v) for k, v in journals.items()},
        "publisher": {
            "name": publisher.name,
            "journals": publisher.journals,
        } if publisher else None,
    }

    FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_state():
    if not FILE_PATH.exists():
        return {}, {}, {}, {}, None

    with open(FILE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    authors = {
        int(key): Author(**value)
        for key, value in data.get("authors", {}).items()
    }

    editors = {
        int(key): Editor(**value)
        for key, value in data.get("editors", {}).items()
    }

    articles = {
        int(key): ScientificArticle(**value)
        for key, value in data.get("articles", {}).items()
    }

    journals = {
        int(key): Journal(**value)
        for key, value in data.get("journals", {}).items()
    }

    publisher_data = data.get("publisher")

    if publisher_data is None:
        publisher = None
    else:
        publisher = PublishingHouse(
            publisher_data["name"],
            publisher_data.get("journals", []),
        )

    return authors, editors, articles, journals, publisher