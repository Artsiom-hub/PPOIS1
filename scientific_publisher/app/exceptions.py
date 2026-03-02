class PublishingError(Exception):
    pass


class InvalidStateTransition(PublishingError):
    pass


class EntityNotFound(PublishingError):
    pass