import json
import os

from classes.author import Author
from classes.reviewer import Editor
from classes.scientific_article import ScientificArticle
from classes.journal import Journal


FILE_PATH = "data/state.json"


def save_state(authors, editors, articles, journals, publisher):

    data = {
        "authors": {k: vars(v) for k, v in authors.items()},
        "editors": {k: vars(v) for k, v in editors.items()},
        "articles": {k: vars(v) for k, v in articles.items()},
        "journals": {k: vars(v) for k, v in journals.items()},
        "publisher": {
            "name": publisher.name,
            "journals": publisher.journals
        }
    }

    os.makedirs("data", exist_ok=True)

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_state():

    if not os.path.exists(FILE_PATH):
        return {}, {}, {}, {}, None

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    authors = {
        int(k): Author(**v)
        for k, v in data["authors"].items()
    }

    editors = {
        int(k): Editor(**v)
        for k, v in data["editors"].items()
    }

    articles = {
        int(k): ScientificArticle(**v)
        for k, v in data["articles"].items()
    }

    journals = {
        int(k): Journal(**v)
        for k, v in data["journals"].items()
    }

    publisher_data = data["publisher"]

    from classes.publisher import PublishingHouse

    publisher = PublishingHouse(
        publisher_data["name"],
        publisher_data["journals"]
    )

    return authors, editors, articles, journals, publisher