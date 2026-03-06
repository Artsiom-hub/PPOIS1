from classes.scientific_article import ScientificArticle
from abc import ABC, abstractmethod


class ArticleSubmission(ABC):

    @abstractmethod
    def submit(self, article: ScientificArticle) -> None:
        pass


class ArticleReview(ABC):

    @abstractmethod
    def review(self, article: ScientificArticle) -> None:
        pass


class LayoutService(ABC):

    @abstractmethod
    def layout(self, article: ScientificArticle) -> None:
        pass


class DistributionService(ABC):

    @abstractmethod
    def distribute(self, edition_id: int) -> None:
        pass