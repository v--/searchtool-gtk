import importlib
import json
import tomllib
import warnings
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

import msgspec
import platformdirs

from .exceptions import SearchToolDeprecationWarning, SearchToolValidationError
from .modes import SearchToolMode


if TYPE_CHECKING:
    import pathlib


class SearchToolModeConfig(msgspec.Struct, forbid_unknown_fields=True):
    name: str
    class_fqn: str = msgspec.field(name='class')
    param: Any = None


class SearchToolConfig(msgspec.Struct, forbid_unknown_fields=True):
    modes: Sequence[SearchToolModeConfig]


ModeMapping = Mapping[str, SearchToolMode]


def build_modes_from_config_file() -> ModeMapping:  # noqa: C901
    raw_config: Mapping[str, Any] | None = None
    config_path: pathlib.Path | None = None

    for config_dir in [platformdirs.site_config_path(), platformdirs.user_config_path()]:
        toml_config_path = config_dir / 'searchtool.toml'
        json_config_path = config_dir / 'searchtool.json'

        if toml_config_path:
            try:
                with open(toml_config_path, 'rb') as file:
                    raw_config = tomllib.load(file)
            except FileNotFoundError:
                pass
            except tomllib.TOMLDecodeError as err:
                raise SearchToolValidationError(f'Cannot decode {toml_config_path!r}') from err
            else:
                config_path = toml_config_path

        if raw_config is None and json_config_path:
            try:
                with open(json_config_path) as file:
                    raw_config = json.load(file)
            except FileNotFoundError:
                pass
            except json.JSONDecodeError as err:
                raise SearchToolValidationError(f'Cannot decode {json_config_path!r}') from err
            else:
                config_path = json_config_path
                warnings.warn(
                    SearchToolDeprecationWarning('JSON configurations are deprecated; consider using searchtool.toml'),
                    stacklevel=2,
                )

    if raw_config is None:
        raise SearchToolValidationError('Cannot find either searchtool.toml or searchtool.json')

    try:
        config = msgspec.convert(raw_config, type=SearchToolConfig)
    except msgspec.ValidationError as err:
        raise SearchToolValidationError(f'Invalid config in {config_path}') from err

    result: dict[str, SearchToolMode] = {}

    for mode_config in config.modes:
        module_name, _, class_name = mode_config.class_fqn.rpartition('.')
        mode_param: Any = None

        try:
            mode_class = getattr(importlib.import_module(module_name), class_name)
        except (ImportError, AttributeError) as err:
            raise SearchToolValidationError(f'Cannot import class {mode_config.class_fqn} required by mode {mode_config.name!r}') from err

        if not issubclass(mode_class, SearchToolMode):
            raise SearchToolValidationError(f'The class {mode_config.class_fqn} required by mode {mode_config.name!r} does not satisfy the <SearchToolMode> protocol')

        try:
            mode_param = mode_class.build_param_class(mode_config.param)
        except Exception as err:
            raise SearchToolValidationError(f'Could not initialize parameters for {mode_config.name!r}') from err

        if mode_config.name in result:
            raise SearchToolValidationError(f'More than one mode has name {mode_config.name!r}')

        result[mode_config.name] = mode_class(mode_param) if mode_param is not None else mode_class()

    return result
