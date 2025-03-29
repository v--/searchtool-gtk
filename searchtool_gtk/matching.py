import unicodedata


def mangle(string: str) -> str:
    """Mangle a string by casefolding and removing accents."""
    return ''.join(
        c for c in unicodedata.normalize('NFKD', string.casefold()) if unicodedata.category(c) != 'Mn'
    )
