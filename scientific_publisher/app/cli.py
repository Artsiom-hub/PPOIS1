from app.repository import ManuscriptRepository
from app.persistence import save, load
from app.services import PublishingService
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
    for manuscript in load():
        repo.add(manuscript)

    service = PublishingService(repo)

    while True:
        print_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                title = input("Title: ")
                authors_raw = input("Authors (comma separated): ")
                authors = [a.strip() for a in authors_raw.split(",")]

                manuscript = service.create_manuscript(title, authors)
                print(f"Created manuscript ID: {manuscript.id}")

            elif choice == "2":
                manuscripts = service.list_manuscripts()
                if not manuscripts:
                    print("No manuscripts found.")

                for m in manuscripts:
                    print(
                        f"ID: {m.id} | "
                        f"Title: {m.title} | "
                        f"Status: {m.status.value}"
                    )

            elif choice == "3":
                manuscript_id = input("Manuscript ID: ")
                service.submit_manuscript(manuscript_id)
                print("Manuscript submitted and sent to review.")

            elif choice == "4":
                manuscript_id = input("Manuscript ID: ")
                reviewer = input("Reviewer name: ")
                decision = input("Decision (accept/reject): ").lower()

                service.add_review(manuscript_id, reviewer, decision)
                print("Review added and decision evaluated.")

            elif choice == "5":
                save(repo.list_all())
                print("State saved. Exiting.")
                break

            else:
                print("Invalid option.")

        except PublishingError as e:
            print(f"Error: {e}")