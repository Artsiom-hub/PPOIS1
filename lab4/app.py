from __future__ import annotations

import io
from contextlib import redirect_stdout
from typing import Callable, TypeVar

from flask import Flask, flash, redirect, render_template, request, url_for

from core import storage
from core.classes.author import Author
from core.classes.electronic_version import ElectronicVersion
from core.classes.journal import Journal
from core.classes.printed_edition import PrintedEdition
from core.classes.publisher import PublishingHouse
from core.classes.reviewer import Editor
from core.classes.scientific_article import ScientificArticle
from core.exceptions import (
    ArticleNotFoundError,
    AuthorNotFoundError,
    EditorNotFoundError,
    InvalidInputError,
    JournalNotFoundError,
)
from core.services import (
    ArticleSubmissionService,
    DistributionServiceImpl,
    ElectronicPublishingService,
    LayoutServiceImpl,
    PeerReviewService,
    PrintService,
)


app = Flask(__name__)
app.secret_key = "ppois-lab4-secret-key"


submission_service = ArticleSubmissionService()
review_service = PeerReviewService()
layout_service = LayoutServiceImpl()
print_service = PrintService()
electronic_service = ElectronicPublishingService()
distribution_service = DistributionServiceImpl()

T = TypeVar("T")


def load_model() -> tuple[
    dict[int, Author],
    dict[int, Editor],
    dict[int, ScientificArticle],
    dict[int, Journal],
    PublishingHouse,
]:
    authors, editors, articles, journals, publisher = storage.load_state()

    if publisher is None:
        publisher = PublishingHouse("International Science Publisher")
        storage.save_state(authors, editors, articles, journals, publisher)

    return authors, editors, articles, journals, publisher


def save_model(
    authors: dict[int, Author],
    editors: dict[int, Editor],
    articles: dict[int, ScientificArticle],
    journals: dict[int, Journal],
    publisher: PublishingHouse,
) -> None:
    storage.save_state(authors, editors, articles, journals, publisher)


def to_int(value: str | None, field_name: str) -> int:
    if value is None or not value.strip():
        raise InvalidInputError(f"Поле '{field_name}' обязательно для заполнения")

    try:
        return int(value)
    except ValueError as exc:
        raise InvalidInputError(f"Поле '{field_name}' должно быть числом") from exc


def get_text(field_name: str) -> str:
    value = request.form.get(field_name, "").strip()

    if not value:
        raise InvalidInputError(f"Поле '{field_name}' обязательно для заполнения")

    return value


def parse_ids(raw_value: str, field_name: str) -> list[int]:
    try:
        ids = [
            int(item.strip())
            for item in raw_value.split(",")
            if item.strip()
        ]
    except ValueError as exc:
        raise InvalidInputError(
            f"Поле '{field_name}' должно содержать числа, разделённые запятыми"
        ) from exc

    if not ids:
        raise InvalidInputError(f"Поле '{field_name}' должно содержать хотя бы один ID")

    return ids


def capture_output(action: Callable[[], T]) -> str:
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        action()

    return buffer.getvalue().strip()


@app.route("/", methods=["GET"])
def index():
    authors, editors, articles, journals, publisher = load_model()

    return render_template(
        "index.html",
        authors=authors,
        editors=editors,
        articles=articles,
        journals=journals,
        publisher=publisher,
    )


@app.route("/authors/add", methods=["POST"])
def add_author():
    authors, editors, articles, journals, publisher = load_model()

    try:
        author_id = to_int(request.form.get("id"), "ID автора")
        name = get_text("name")
        affiliation = get_text("affiliation")
        email = get_text("email")

        if author_id in authors:
            raise InvalidInputError("Автор с таким ID уже существует")

        authors[author_id] = Author(
            id=author_id,
            name=name,
            affiliation=affiliation,
            email=email,
        )

        save_model(authors, editors, articles, journals, publisher)
        flash("Автор успешно добавлен", "success")

    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("index"))


@app.route("/editors/add", methods=["POST"])
def add_editor():
    authors, editors, articles, journals, publisher = load_model()

    try:
        editor_id = to_int(request.form.get("id"), "ID редактора")
        name = get_text("name")
        field = get_text("field")

        if editor_id in editors:
            raise InvalidInputError("Редактор с таким ID уже существует")

        editors[editor_id] = Editor(
            id=editor_id,
            name=name,
            field=field,
        )

        save_model(authors, editors, articles, journals, publisher)
        flash("Редактор успешно добавлен", "success")

    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("index"))


@app.route("/articles/submit", methods=["POST"])
def submit_article():
    authors, editors, articles, journals, publisher = load_model()

    try:
        article_id = to_int(request.form.get("id"), "ID статьи")
        title = get_text("title")
        abstract = get_text("abstract")
        author_ids_raw = get_text("author_ids")

        if article_id in articles:
            raise InvalidInputError("Статья с таким ID уже существует")

        author_ids = parse_ids(author_ids_raw, "ID авторов")

        article_authors: list[str] = []

        for author_id in author_ids:
            author = authors.get(author_id)

            if author is None:
                raise AuthorNotFoundError(f"Автор с ID {author_id} не найден")

            article_authors.append(author.name)

        article = ScientificArticle(
            id=article_id,
            title=title,
            authors=article_authors,
            abstract=abstract,
        )

        articles[article_id] = article
        capture_output(lambda: submission_service.submit(article))

        save_model(authors, editors, articles, journals, publisher)
        flash("Статья успешно подана", "success")

    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("index"))


@app.route("/articles/review", methods=["POST"])
def review_article():
    authors, editors, articles, journals, publisher = load_model()

    try:
        article_id = to_int(request.form.get("article_id"), "ID статьи")
        editor_id = to_int(request.form.get("editor_id"), "ID редактора")

        article = articles.get(article_id)

        if article is None:
            raise ArticleNotFoundError("Статья не найдена")

        editor = editors.get(editor_id)

        if editor is None:
            raise EditorNotFoundError("Редактор не найден")

        capture_output(lambda: review_service.review(article, editor))
        article.change_status("reviewed")

        save_model(authors, editors, articles, journals, publisher)
        flash("Статья успешно отрецензирована", "success")

    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("index"))


@app.route("/articles/layout", methods=["POST"])
def layout_article():
    authors, editors, articles, journals, publisher = load_model()

    try:
        article_id = to_int(request.form.get("article_id"), "ID статьи")

        article = articles.get(article_id)

        if article is None:
            raise ArticleNotFoundError("Статья не найдена")

        capture_output(lambda: layout_service.layout(article))
        article.change_status("layout_ready")

        save_model(authors, editors, articles, journals, publisher)
        flash("Статья успешно подготовлена к публикации", "success")

    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("index"))


@app.route("/journals/add", methods=["POST"])
def add_journal():
    authors, editors, articles, journals, publisher = load_model()

    try:
        journal_id = to_int(request.form.get("id"), "ID журнала")
        name = get_text("name")
        field = get_text("field")

        if journal_id in journals:
            raise InvalidInputError("Журнал с таким ID уже существует")

        journals[journal_id] = Journal(
            id=journal_id,
            name=name,
            field=field,
        )

        if journal_id not in publisher.journals:
            publisher.add_journal(journal_id)

        save_model(authors, editors, articles, journals, publisher)
        flash("Журнал успешно добавлен в издательство", "success")

    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("index"))


@app.route("/journals/add-article", methods=["POST"])
def add_article_to_journal():
    authors, editors, articles, journals, publisher = load_model()

    try:
        article_id = to_int(request.form.get("article_id"), "ID статьи")
        journal_id = to_int(request.form.get("journal_id"), "ID журнала")

        article = articles.get(article_id)

        if article is None:
            raise ArticleNotFoundError("Статья не найдена")

        journal = journals.get(journal_id)

        if journal is None:
            raise JournalNotFoundError("Журнал не найден")

        if article_id in journal.articles:
            raise InvalidInputError("Эта статья уже добавлена в журнал")

        journal.add_article(article_id)

        save_model(authors, editors, articles, journals, publisher)
        flash(
            f"Статья '{article.title}' добавлена в журнал '{journal.name}'",
            "success",
        )

    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("index"))


@app.route("/journals/print", methods=["POST"])
def print_journal():
    authors, editors, articles, journals, publisher = load_model()

    try:
        journal_id = to_int(request.form.get("journal_id"), "ID журнала")
        issue_number = to_int(request.form.get("issue_number"), "Номер выпуска")
        copies = to_int(request.form.get("copies"), "Количество экземпляров")

        journal = journals.get(journal_id)

        if journal is None:
            raise JournalNotFoundError("Журнал не найден")

        edition = PrintedEdition(
            journal_id=journal_id,
            issue_number=issue_number,
            copies=copies,
            articles=journal.articles,
        )

        message = capture_output(lambda: print_service.print_journal(edition))
        flash(message or "Печатный выпуск успешно сформирован", "success")

    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("index"))


@app.route("/journals/electronic", methods=["POST"])
def publish_electronic():
    authors, editors, articles, journals, publisher = load_model()

    try:
        journal_id = to_int(request.form.get("journal_id"), "ID журнала")
        url = get_text("url")

        if journal_id not in journals:
            raise JournalNotFoundError("Журнал не найден")

        version = ElectronicVersion(
            journal_id=journal_id,
            url=url,
        )

        message = capture_output(lambda: electronic_service.release(version))
        flash(message or "Электронная версия успешно выпущена", "success")

    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("index"))


@app.route("/distribution", methods=["POST"])
def distribute():
    try:
        edition_id = to_int(request.form.get("edition_id"), "ID выпуска")

        message = capture_output(
            lambda: distribution_service.distribute(edition_id)
        )

        flash(message or "Выпуск успешно распространён", "success")

    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)