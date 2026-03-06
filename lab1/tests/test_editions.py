from classes.printed_edition import PrintedEdition
from classes.electronic_version import ElectronicVersion


def test_print_issue():

    edition = PrintedEdition(
        journal_id=1,
        issue_number=1,
        copies=100,
        articles=[1, 2]
    )

    result = edition.print_issue()

    assert "Printed 100 copies" in result
    assert "Article ID 1" in result


def test_electronic_publish():

    version = ElectronicVersion(1, "https://journal.org")

    result = version.publish()

    assert "https://journal.org" in result