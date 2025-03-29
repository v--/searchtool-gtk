from .pipe import PipeMode
from ..pydantic_helpers import StrictPydanticModel
from ..matching import mangle
from typing import Any


class ClipHistModeConfig(StrictPydanticModel):
    loose_matching: bool = False


class ClipHistMode(PipeMode):
    config: ClipHistModeConfig

    @classmethod
    def build_param_class(cls, param: Any) -> ClipHistModeConfig:
        if param is None:
            return ClipHistModeConfig()

        return ClipHistModeConfig.model_validate(param)

    def __init__(self, config: ClipHistModeConfig) -> None:
        super().__init__()
        self.config = config

    def get_main_item_label(self, item: str):
        try:
            i, text = item.split('\t', maxsplit=1)
        except ValueError:
            return ''
        else:
            return text

    def match_item(self, item: str, filter_string: str):
        if self.config.loose_matching:
            return mangle(filter_string) in mangle(item)

        return super().match_item(item, filter_string)
