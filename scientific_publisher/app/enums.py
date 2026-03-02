from enum import Enum


class ManuscriptStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REVISION = "REVISION"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"


class ReviewStatus(str, Enum):
    ASSIGNED = "ASSIGNED"
    SUBMITTED = "SUBMITTED"