from dataclasses import dataclass

from typing import List


@dataclass
class PrintedEdition:
    journal_id: int
    issue_number: int
    copies: int
    articles: List[int]

    def print_issue(self) -> str:

        result = f"Printed {self.copies} copies of journal issue {self.issue_number}\n"

        result += "Articles in issue:\n"

        for article in self.articles:
            result += f"- Article ID {article}\n"

        return result