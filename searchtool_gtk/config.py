from pathlib import Path
from typing import Any, Annotated
from collections.abc import Mapping, Sequence
import importlib
import json
import pydantic

from .exceptions import SearchToolValidationError
from .mode import SearchToolMode
from .pydantic_helpers import StrictPydanticModel


class SearchToolModeConfig(StrictPydanticModel):
    name: str
    class_fqn: Annotated[str, pydantic.Field(alias='class')]
    param: Any = None


class SearchToolConfig(StrictPydanticModel):
    modes: Sequence[SearchToolModeConfig]


ModeDict = Mapping[str, SearchToolMode]


def build_modes_from_file(path: Path) -> ModeDict:
    with open(path) as file:
        try:
            raw_config = json.load(file)
        except json.JSONDecodeError as err:
            raise SearchToolValidationError(f'Cannot decode {path}: {err}')

        try:
            config = SearchToolConfig.model_validate(raw_config, strict=True)
        except pydantic.ValidationError as err:
            raise SearchToolValidationError(f'Invalid config in {path}: {err}')

    result: dict[str, SearchToolMode] = {}

    for mode_config in config.modes:
        module_name, _, class_name = mode_config.class_fqn.rpartition('.')
        mode_param: Any = None

        try:
            mode_class = getattr(importlib.import_module(module_name), class_name)
        except (ImportError, AttributeError):
            raise SearchToolValidationError(f'Cannot import class {mode_config.class_fqn} required by mode {repr(mode_config.name)}')

        if not issubclass(mode_class, SearchToolMode):
            raise SearchToolValidationError(f'The class {mode_config.class_fqn} required by mode {repr(mode_config.name)} does not satisfy the <SearchToolMode> protocol')

        try:
            mode_param = mode_class.build_param_class(mode_config.param)
        except Exception as err:
            raise SearchToolValidationError(f'Could not initialize parameters for {repr(mode_config.name)}: {err}')

        if mode_config.name in result:
            raise SearchToolValidationError(f'More than one mode has name {repr(mode_config.name)}')

        result[mode_config.name] = mode_class(mode_param) if mode_param is not None else mode_class()

    return result
