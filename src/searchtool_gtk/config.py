import importlib
import tomllib
from collections.abc import Hashable, Mapping
from typing import Any

import msgspec
from platformdirs import PlatformDirs

from .exceptions import SearchToolValidationError
from .modes import SearchToolMode


ModeMapping = Mapping[str, SearchToolMode[Hashable]]


# ruff: ignore[complex-structure]
def load_modes_from_config_file() -> ModeMapping:
    dirs = PlatformDirs('searchtool', appauthor=False)
    raw_config: Mapping[str, Hashable] | None = None

    for config_dir in dirs.iter_config_paths():
        toml_config_path = config_dir / 'config.toml'

        try:
            with open(toml_config_path, 'rb') as file:
                raw_config = tomllib.load(file)
        except FileNotFoundError:
            pass
        except tomllib.TOMLDecodeError as err:
            raise SearchToolValidationError(f'Cannot decode {toml_config_path!r}') from err
        else:
            config_path = toml_config_path
            break

    if raw_config is None:
        raise SearchToolValidationError('Cannot find a configuration for searchtool')

    modes_raw = raw_config.get('modes')

    if not isinstance(modes_raw, dict):
        raise SearchToolValidationError(f"The config at {config_path} must have a 'modes' table.")

    modes: dict[str, SearchToolMode[Hashable]] = {}

    for mode_name, mode_config_raw in modes_raw.items():
        if not isinstance(mode_config_raw, dict):
            raise SearchToolValidationError(f'The configuration for mode {mode_name!r} must be a table.')

        class_fqn = mode_config_raw.pop('class', None)

        if not isinstance(class_fqn, str):
            raise SearchToolValidationError(f"The 'class' property in the configuration for mode {mode_name!r} must be a string.")

        module_name, _, class_name = class_fqn.rpartition('.')

        try:
            mode_class = getattr(importlib.import_module(module_name), class_name)
        except (ImportError, AttributeError) as err:
            raise SearchToolValidationError(f'Cannot import class {class_fqn} required by mode {mode_name!r}') from err

        if not issubclass(mode_class, SearchToolMode):
            raise SearchToolValidationError(f'The class {class_fqn} required by mode {mode_name!r} does not satisfy the SearchToolMode protocol')

        mode_kwargs = dict[str, Any]()

        if config_class := getattr(mode_class, '__searchtool_config_type__', None):
            try:
                mode_kwargs['config'] = msgspec.convert(mode_config_raw, type=config_class)
            except Exception as err:
                raise SearchToolValidationError(f'Could not load config for {mode_name!r}') from err

        try:
            modes[mode_name] = mode_class(**mode_kwargs)
        except Exception as err:
            raise SearchToolValidationError(f'Could not initialize mode for {mode_name!r}') from err

    return modes
