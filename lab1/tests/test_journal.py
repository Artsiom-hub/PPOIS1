from classes.journal import Journal


def test_add_article_to_journal():

    journal = Journal(1, "Science Journal", "AI")

    journal.add_article(10)

    assert 10 in journal.articles