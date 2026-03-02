from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from uuid import uuid4
from app.enums import ManuscriptStatus, ReviewStatus
from app.exceptions import InvalidStateTransition


@dataclass
class Review:
    reviewer: str
    recommendation: str | None = None
    status: ReviewStatus = ReviewStatus.ASSIGNED

    def submit(self, recommendation: str) -> None:
        if self.status != ReviewStatus.ASSIGNED:
            raise InvalidStateTransition("Review already submitted")
        self.recommendation = recommendation
        self.status = ReviewStatus.SUBMITTED


@dataclass
class Manuscript:
    title: str
    authors: List[str]
    id: str = field(default_factory=lambda: str(uuid4()))
    status: ManuscriptStatus = ManuscriptStatus.DRAFT
    reviews: List[Review] = field(default_factory=list)

    def submit(self) -> None:
        if self.status != ManuscriptStatus.DRAFT:
            raise InvalidStateTransition("Only draft can be submitted")
        self.status = ManuscriptStatus.SUBMITTED

    def start_review(self) -> None:
        if self.status != ManuscriptStatus.SUBMITTED:
            raise InvalidStateTransition("Must be submitted first")
        self.status = ManuscriptStatus.UNDER_REVIEW

    def add_review(self, review: Review) -> None:
        self.reviews.append(review)

    def make_decision(self) -> None:
        if self.status != ManuscriptStatus.UNDER_REVIEW:
            raise InvalidStateTransition("Not under review")

        submitted = [r for r in self.reviews if r.status == ReviewStatus.SUBMITTED]
        if len(submitted) < 2:
            raise InvalidStateTransition("Need at least 2 reviews")

        accepts = [r for r in submitted if r.recommendation == "accept"]
        rejects = [r for r in submitted if r.recommendation == "reject"]

        if len(accepts) > len(rejects):
            self.status = ManuscriptStatus.ACCEPTED
        else:
            self.status = ManuscriptStatus.REJECTED