class PublishingError(Exception):
    """Базовая ошибка системы издательства"""
    pass


class AuthorNotFoundError(PublishingError):
    pass


class EditorNotFoundError(PublishingError):
    pass


class ArticleNotFoundError(PublishingError):
    pass


class JournalNotFoundError(PublishingError):
    pass


class InvalidInputError(PublishingError):
    pass