from classes.scientific_article import ScientificArticle
from classes.printed_edition import PrintedEdition
from classes.electronic_version import ElectronicVersion
from classes.reviewer import Editor

from interface import (
    ArticleSubmission,
    ArticleReview,
    LayoutService,
    DistributionService
)
class ArticleSubmissionService(ArticleSubmission):

    def __init__(self):
        self.articles = {}

    def submit(self, article: ScientificArticle) -> None:
        self.articles[article.id] = article
        article.change_status("submitted")
        print(f"Article '{article.title}' submitted")





class PeerReviewService:
    def review(self, article: ScientificArticle, editor: Editor) -> None:
        article.change_status("reviewed")
        print(editor.review_article(article.title))

class LayoutServiceImpl(LayoutService):

    def layout(self, article: ScientificArticle) -> None:
        article.change_status("layout_ready")
        print(f"Article '{article.title}' prepared for publishing")

class PrintService:

    def print_journal(self, edition: PrintedEdition) -> None:
        print(edition.print_issue())

class ElectronicPublishingService:

    def release(self, version: ElectronicVersion) -> None:
        print(version.publish())

class DistributionServiceImpl(DistributionService):

    def distribute(self, edition_id: int) -> None:
        print(f"Edition {edition_id} distributed to libraries")