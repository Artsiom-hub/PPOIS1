from __future__ import annotations

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


submission_service = ArticleSubmissionService()
review_service = PeerReviewService()
layout_service = LayoutServiceImpl()
print_service = PrintService()
electronic_service = ElectronicPublishingService()
distribution_service = DistributionServiceImpl()


def load_model():
    authors, editors, articles, journals, publisher = storage.load_state()

    if publisher is None:
        publisher = PublishingHouse("International Science Publisher")
        storage.save_state(authors, editors, articles, journals, publisher)

    return authors, editors, articles, journals, publisher


def save_model(authors, editors, articles, journals, publisher) -> None:
    storage.save_state(authors, editors, articles, journals, publisher)


def read_int(prompt: str) -> int:
    value = input(prompt).strip()

    if not value:
        raise InvalidInputError("Значение не может быть пустым")

    try:
        return int(value)
    except ValueError as exc:
        raise InvalidInputError("Значение должно быть числом") from exc


def read_text(prompt: str) -> str:
    value = input(prompt).strip()

    if not value:
        raise InvalidInputError("Значение не может быть пустым")

    return value


def read_ids(prompt: str) -> list[int]:
    raw_value = read_text(prompt)

    try:
        ids = [
            int(item.strip())
            for item in raw_value.split(",")
            if item.strip()
        ]
    except ValueError as exc:
        raise InvalidInputError(
            "ID должны быть числами, разделёнными запятыми"
        ) from exc

    if not ids:
        raise InvalidInputError("Нужно указать хотя бы один ID")

    return ids


def add_author() -> None:
    authors, editors, articles, journals, publisher = load_model()

    author_id = read_int("ID автора: ")
    name = read_text("Имя автора: ")
    affiliation = read_text("Организация: ")
    email = read_text("Email: ")

    if author_id in authors:
        raise InvalidInputError("Автор с таким ID уже существует")

    authors[author_id] = Author(
        id=author_id,
        name=name,
        affiliation=affiliation,
        email=email,
    )

    save_model(authors, editors, articles, journals, publisher)
    print("Автор успешно добавлен")


def add_editor() -> None:
    authors, editors, articles, journals, publisher = load_model()

    editor_id = read_int("ID редактора: ")
    name = read_text("Имя редактора: ")
    field = read_text("Научная область: ")

    if editor_id in editors:
        raise InvalidInputError("Редактор с таким ID уже существует")

    editors[editor_id] = Editor(
        id=editor_id,
        name=name,
        field=field,
    )

    save_model(authors, editors, articles, journals, publisher)
    print("Редактор успешно добавлен")


def submit_article() -> None:
    authors, editors, articles, journals, publisher = load_model()

    article_id = read_int("ID статьи: ")
    title = read_text("Название статьи: ")
    abstract = read_text("Аннотация: ")
    author_ids = read_ids("ID авторов через запятую: ")

    if article_id in articles:
        raise InvalidInputError("Статья с таким ID уже существует")

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
    submission_service.submit(article)

    save_model(authors, editors, articles, journals, publisher)


def review_article() -> None:
    authors, editors, articles, journals, publisher = load_model()

    article_id = read_int("ID статьи для рецензии: ")
    editor_id = read_int("ID редактора: ")

    article = articles.get(article_id)

    if article is None:
        raise ArticleNotFoundError("Статья не найдена")

    editor = editors.get(editor_id)

    if editor is None:
        raise EditorNotFoundError("Редактор не найден")

    review_service.review(article, editor)

    save_model(authors, editors, articles, journals, publisher)


def layout_article() -> None:
    authors, editors, articles, journals, publisher = load_model()

    article_id = read_int("ID статьи для верстки: ")

    article = articles.get(article_id)

    if article is None:
        raise ArticleNotFoundError("Статья не найдена")

    layout_service.layout(article)

    save_model(authors, editors, articles, journals, publisher)


def add_journal() -> None:
    authors, editors, articles, journals, publisher = load_model()

    journal_id = read_int("ID журнала: ")
    name = read_text("Название журнала: ")
    field = read_text("Научная область: ")

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
    print("Журнал успешно добавлен в издательство")


def add_article_to_journal() -> None:
    authors, editors, articles, journals, publisher = load_model()

    article_id = read_int("ID статьи: ")
    journal_id = read_int("ID журнала: ")

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
    print(f"Статья '{article.title}' добавлена в журнал '{journal.name}'")


def print_journal() -> None:
    authors, editors, articles, journals, publisher = load_model()

    journal_id = read_int("ID журнала: ")
    issue_number = read_int("Номер выпуска: ")
    copies = read_int("Количество экземпляров: ")

    journal = journals.get(journal_id)

    if journal is None:
        raise JournalNotFoundError("Журнал не найден")

    edition = PrintedEdition(
        journal_id=journal_id,
        issue_number=issue_number,
        copies=copies,
        articles=journal.articles,
    )

    print_service.print_journal(edition)


def publish_electronic() -> None:
    authors, editors, articles, journals, publisher = load_model()

    journal_id = read_int("ID журнала: ")
    url = read_text("URL электронной версии: ")

    if journal_id not in journals:
        raise JournalNotFoundError("Журнал не найден")

    version = ElectronicVersion(
        journal_id=journal_id,
        url=url,
    )

    electronic_service.release(version)


def distribute() -> None:
    edition_id = read_int("ID выпуска: ")
    distribution_service.distribute(edition_id)


def show_state() -> None:
    authors, editors, articles, journals, publisher = load_model()

    print("\n===== ТЕКУЩЕЕ СОСТОЯНИЕ МОДЕЛИ =====")

    print("\nИздательство:")
    if publisher:
        print(f"Название: {publisher.name}")
        print(f"ID журналов: {publisher.journals}")
    else:
        print("Издательство не создано")

    print("\nАвторы:")
    if authors:
        for author_id, author in authors.items():
            print(
                f"{author_id}. {author.name}, "
                f"{author.affiliation}, {author.email}"
            )
    else:
        print("Авторы отсутствуют")

    print("\nРедакторы:")
    if editors:
        for editor_id, editor in editors.items():
            print(f"{editor_id}. {editor.name}, область: {editor.field}")
    else:
        print("Редакторы отсутствуют")

    print("\nСтатьи:")
    if articles:
        for article_id, article in articles.items():
            print(
                f"{article_id}. {article.title}; "
                f"авторы: {', '.join(article.authors)}; "
                f"статус: {article.status}"
            )
            print(f"   Аннотация: {article.abstract}")
    else:
        print("Статьи отсутствуют")

    print("\nЖурналы:")
    if journals:
        for journal_id, journal in journals.items():
            print(
                f"{journal_id}. {journal.name}; "
                f"область: {journal.field}; "
                f"ID статей: {journal.articles}"
            )
    else:
        print("Журналы отсутствуют")


def show_menu() -> None:
    print("\n===== СИСТЕМА ИЗДАТЕЛЬСТВА =====")
    print("1. Добавить автора")
    print("2. Добавить редактора")
    print("3. Подать статью")
    print("4. Рецензировать статью")
    print("5. Верстка статьи")
    print("6. Добавить журнал")
    print("7. Добавить статью в журнал")
    print("8. Печать журнала")
    print("9. Выпуск электронной версии")
    print("10. Распространение выпуска")
    print("11. Показать текущее состояние модели")
    print("0. Выход")


def handle_choice(choice: str) -> bool:
    if choice == "1":
        add_author()
    elif choice == "2":
        add_editor()
    elif choice == "3":
        submit_article()
    elif choice == "4":
        review_article()
    elif choice == "5":
        layout_article()
    elif choice == "6":
        add_journal()
    elif choice == "7":
        add_article_to_journal()
    elif choice == "8":
        print_journal()
    elif choice == "9":
        publish_electronic()
    elif choice == "10":
        distribute()
    elif choice == "11":
        show_state()
    elif choice == "0":
        print("Выход из программы")
        return False
    else:
        raise InvalidInputError("Неверный пункт меню")

    return True


def main() -> None:
    while True:
        show_menu()
        choice = input("Выберите действие: ").strip()

        try:
            should_continue = handle_choice(choice)

            if not should_continue:
                break

        except Exception as exc:
            print("Ошибка:", exc)


if __name__ == "__main__":
    main()