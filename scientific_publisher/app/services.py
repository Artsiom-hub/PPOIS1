from app.models import Manuscript, Review
from app.repository import ManuscriptRepository
from app.exceptions import PublishingError


class PublishingService:

    def __init__(self, repository: ManuscriptRepository) -> None:
        self._repository = repository

    def create_manuscript(
        self,
        title: str,
        authors: list[str]
    ) -> Manuscript:

        manuscript = Manuscript(title=title, authors=authors)
        self._repository.add(manuscript)
        return manuscript

    def submit_manuscript(self, manuscript_id: str) -> None:
        manuscript = self._repository.get(manuscript_id)
        manuscript.submit()
        manuscript.start_review()

    def add_review(
        self,
        manuscript_id: str,
        reviewer: str,
        decision: str
    ) -> None:

        manuscript = self._repository.get(manuscript_id)

        review = Review(reviewer=reviewer)
        review.submit(decision)

        manuscript.add_review(review)
        manuscript.make_decision()

    def list_manuscripts(self) -> list[Manuscript]:
        return self._repository.list_all()