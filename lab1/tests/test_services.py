from classes.scientific_article import ScientificArticle
from classes.reviewer import Editor

from services import (
    ArticleSubmissionService,
    PeerReviewService,
    LayoutServiceImpl
)


def test_article_submission():

    service = ArticleSubmissionService()

    article = ScientificArticle(
        1,
        "AI Research",
        ["Ivan Petrov"],
        "AI study"
    )

    service.submit(article)

    assert article.status == "submitted"


def test_peer_review():

    service = PeerReviewService()

    editor = Editor(1, "Dr Smith", "AI")

    article = ScientificArticle(
        1,
        "AI Research",
        ["Ivan Petrov"],
        "AI study"
    )

    service.review(article, editor)

    assert article.status == "reviewed"


def test_layout_service():

    service = LayoutServiceImpl()

    article = ScientificArticle(
        1,
        "AI Research",
        ["Ivan Petrov"],
        "AI study"
    )

    service.layout(article)

    assert article.status == "layout_ready"