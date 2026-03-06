from classes.scientific_article import ScientificArticle


def test_article_creation():

    article = ScientificArticle(
        id=1,
        title="AI Research",
        authors=["Ivan Petrov"],
        abstract="Study about AI"
    )

    assert article.status == "submitted"
    assert article.title == "AI Research"


def test_article_status_change():

    article = ScientificArticle(
        1,
        "AI Research",
        ["Ivan Petrov"],
        "AI study"
    )

    article.change_status("reviewed")

    assert article.status == "reviewed"