class SearchToolException(Exception):
    pass


class SearchToolError(SearchToolException):
    pass


# Integrity errors cover developer errors
class SearchToolIntegrityError(SearchToolError):
    pass


# Validation errors cover user errors
class SearchToolValidationError(SearchToolError):
    pass
