from app.models import Manuscript, Review
from app.repository import ManuscriptRepository
from app.persistence import save, load
from app.exceptions import PublishingError


def print_menu() -> None:
    print("\n=== Scientific Publisher CLI ===")
    print("1. Create manuscript")
    print("2. List manuscripts")
    print("3. Submit manuscript")
    print("4. Add review")
    print("5. Exit")


def run_cli() -> None:
    repo = ManuscriptRepository()

    # загрузка состояния
    for m in load():
        repo.add(m)

    while True:
        print_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                title = input("Title: ")
                authors = input("Authors (comma separated): ").split(",")
                authors = [a.strip() for a in authors]

                manuscript = Manuscript(title=title, authors=authors)
                repo.add(manuscript)

                print(f"Created manuscript ID: {manuscript.id}")

            elif choice == "2":
                manuscripts = repo.list_all()
                if not manuscripts:
                    print("No manuscripts found.")
                for m in manuscripts:
                    print(
                        f"ID: {m.id} | "
                        f"Title: {m.title} | "
                        f"Status: {m.status}"
                    )

            elif choice == "3":
                manuscript_id = input("Manuscript ID: ")
                manuscript = repo.get(manuscript_id)
                manuscript.submit()
                manuscript.start_review()
                print("Manuscript submitted and sent to review.")

            elif choice == "4":
                manuscript_id = input("Manuscript ID: ")
                reviewer = input("Reviewer name: ")
                decision = input("Decision (accept/reject): ")

                manuscript = repo.get(manuscript_id)
                review = Review(reviewer=reviewer)
                review.submit(decision)

                manuscript.add_review(review)
                manuscript.make_decision()

                print("Review added and decision evaluated.")

            elif choice == "5":
                save(repo.list_all())
                print("State saved. Exiting.")
                break

            else:
                print("Invalid option.")

        except PublishingError as e:
            print(f"Error: {e}")