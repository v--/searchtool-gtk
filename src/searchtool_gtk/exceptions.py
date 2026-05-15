class SearchToolException(Exception):
    pass


class SearchToolError(SearchToolException):
    pass


class SearchToolIntegrityError(SearchToolError):
    """An error class for internal errors."""


class SearchToolValidationError(SearchToolError):
    """An error class for user errors."""


class SearchToolWarning(Warning):
    pass


class SearchToolDeprecationWarning(DeprecationWarning, SearchToolWarning):
    pass
