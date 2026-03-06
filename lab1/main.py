from classes.author import Author
from storage import save_state, load_state
from classes.scientific_article import ScientificArticle
from classes.printed_edition import PrintedEdition
from classes.electronic_version import ElectronicVersion
from classes.reviewer import Editor
from classes.journal import Journal
from classes.publisher import PublishingHouse
from exceptions import (
    AuthorNotFoundError,
    EditorNotFoundError,
    ArticleNotFoundError,
    JournalNotFoundError,
    InvalidInputError
)

from services import (
    ArticleSubmissionService,
    PeerReviewService,
    LayoutServiceImpl,
    PrintService,
    ElectronicPublishingService,
    DistributionServiceImpl
)

authors, editors, articles, journals, publisher = load_state()

if publisher is None:
    publisher = PublishingHouse("International Science Publisher")

submission_service = ArticleSubmissionService()
review_service = PeerReviewService()
layout_service = LayoutServiceImpl()
print_service = PrintService()
electronic_service = ElectronicPublishingService()
distribution_service = DistributionServiceImpl()


def add_journal():
    try:
        id_ = int(input("ID журнала: "))
        name = input("Название журнала: ")
        field = input("Научная область: ")

        journal = Journal(id_, name, field)
        journals[id_] = journal

        publisher.add_journal(id_)

        print("Журнал добавлен в издательство")
        save_state(authors, editors, articles, journals, publisher)

    except Exception as e:
        print("Ошибка:", e)

def add_author():
    try:
        id_ = int(input("ID автора: "))
        name = input("Имя автора: ")
        affiliation = input("Организация: ")
        email = input("Email: ")

        author = Author(id_, name, affiliation, email)
        authors[id_] = author
        save_state(authors, editors, articles, journals, publisher)
        print("Автор успешно добавлен")

    except Exception as e:
        print("Ошибка:", e)

def add_article_to_journal():
    try:
        article_id = int(input("ID статьи: "))
        journal_id = int(input("ID журнала: "))

        article = articles.get(article_id)
        journal = journals.get(journal_id)

        if not article:
            raise ArticleNotFoundError("Статья не найдена")

        if not journal:
            raise JournalNotFoundError("Журнал не найден")

        journal.add_article(article_id)

        print(f"Статья '{article.title}' добавлена в журнал '{journal.name}'")
        save_state(authors, editors, articles, journals, publisher)

    except Exception as e:
        print("Ошибка:", e)

def submit_article():
    try:
        id_ = int(input("ID статьи: "))
        title = input("Название статьи: ")
        abstract = input("Аннотация: ")

        print("Введите ID авторов через запятую")
        ids = input("Авторы: ").split(",")

        article_authors = []

        for i in ids:
            a = authors.get(int(i.strip()))
            if a:
                article_authors.append(a.name)

        article = ScientificArticle(
            id=id_,
            title=title,
            authors=article_authors,
            abstract=abstract
        )

        articles[id_] = article
        submission_service.submit(article)
        save_state(authors, editors, articles, journals, publisher)


    except (InvalidInputError, AuthorNotFoundError) as e:
        print("Ошибка:", e)


def review_article():
    try:
        article_id = int(input("ID статьи для рецензии: "))
        editor_id = int(input("ID редактора: "))

        article = articles.get(article_id)
        editor = editors.get(editor_id)

        if not article:
            raise ArticleNotFoundError("Статья не найдена")

        if not editor:
            raise EditorNotFoundError("Редактор не найден")

        review_service.review(article, editor)

    except ValueError:
        print("Ошибка: ID должен быть числом")

    except (ArticleNotFoundError, EditorNotFoundError) as e:
        print("Ошибка:", e)


def layout_article():
    try:
        id_ = int(input("ID статьи для верстки: "))
        article = articles.get(id_)

        if not article:
            raise ArticleNotFoundError("Статья не найдена")

        layout_service.layout(article)

    except Exception as e:
        print("Ошибка:", e)


def print_journal():
    try:
        journal_id = int(input("ID журнала: "))
        issue = int(input("Номер выпуска: "))
        copies = int(input("Количество экземпляров: "))

        journal = journals.get(journal_id)

        if not journal:
            raise JournalNotFoundError("Журнал не найден")

        edition = PrintedEdition(
            journal_id,
            issue,
            copies,
            journal.articles
        )

        print_service.print_journal(edition)

    except Exception as e:
        print("Ошибка:", e)




def add_editor():
    try:
        id_ = int(input("ID редактора: "))
        name = input("Имя редактора: ")
        field = input("Область редактора: ")

        editor = Editor(id_, name, field)
        editors[id_] = editor

        print("Редактор успешно добавлен")
        save_state(authors, editors, articles, journals, publisher)
    except Exception as e:
        print("Ошибка:", e)

def publish_electronic():
    try:
        journal_id = int(input("ID журнала: "))
        url = input("URL электронной версии: ")

        version = ElectronicVersion(journal_id, url)
        electronic_service.release(version)

    except Exception as e:
        print("Ошибка:", e)


def distribute():
    try:
        edition_id = int(input("ID выпуска: "))
        distribution_service.distribute(edition_id)

    except Exception as e:
        print("Ошибка:", e)


def show_menu():
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
    print("0. Выход")


def main():
    while True:

        show_menu()

        choice = input("Выберите действие: ")

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

        else:
            raise InvalidInputError("Неверный пункт меню")


if __name__ == "__main__":
    main()