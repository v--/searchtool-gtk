from typing import override

from ..collation import StringCollator
from ..pydantic_helpers import StrictPydanticModel
from .pipe import PipeMode


class ClipHistModeConfig(StrictPydanticModel):
    icu_locale: str | None = None
    icu_strength: int = 0


class ClipHistMode(PipeMode[ClipHistModeConfig]):
    config: ClipHistModeConfig

    @classmethod
    def build_param_class(cls, param: object) -> ClipHistModeConfig:
        if param is None:
            return ClipHistModeConfig()

        return ClipHistModeConfig.model_validate(param)

    def __init__(self, config: ClipHistModeConfig) -> None:
        super().__init__()
        self.config = config

    @override
    def get_collator(self) -> StringCollator:
        return StringCollator(self.config.icu_locale, self.config.icu_strength)

    @override
    def get_main_item_label(self, item: str):
        try:
            i, text = item.split('\t', maxsplit=1)
        except ValueError:
            return ''
        else:
            return text
