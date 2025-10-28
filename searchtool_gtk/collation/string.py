from typing import override

import icu

from .base import SearchToolCollator


def normalize_icu_locale(locale: icu.Locale | str | None = None) -> icu.Locale:
    match locale:
        case icu.Locale():
            return locale

        case str():
            return icu.Locale(locale)

        case _:
            return icu.Locale()


class StringCollator(SearchToolCollator[str]):
    icu_collator: icu.Collator

    def __init__(self, locale: icu.Locale | str | None = None, strength: int = icu.Collator.PRIMARY):
        icu_locale = normalize_icu_locale(locale)
        self.icu_collator = icu.Collator.createInstance(icu_locale)
        self.icu_collator.setStrength(strength)

    @override
    def compare(self, a: str, b: str) -> int:
        return self.icu_collator.compare(a, b)

    @override
    def match_item(self, item: str, filter_string: str) -> bool:
        ss = icu.StringSearch(filter_string, item, self.icu_collator)
        return ss.first() != -1
