from classes.author import Author


def test_author_creation():
    author = Author(1, "Ivan Petrov", "MIT", "ivan@mail.com")

    assert author.id == 1
    assert author.name == "Ivan Petrov"
    assert author.affiliation == "MIT"
    assert author.email == "ivan@mail.com"