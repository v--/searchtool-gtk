from __future__ import annotations
from pathlib import Path
import importlib
import json

import jsonschema

from .exceptions import SearchToolValidationError
from .mode import SearchToolMode


CONFIG_SCHEMA = {
    'type': 'object',
    'properties': {
        'modes': {
            'type': 'array',
            'elements': {
                'type': 'object',
                'properties': {
                    'name': { 'type': 'string' },
                    'param': {},
                    'mode_class': { 'type': 'string' }
                },
                'requiredProperties': ['name', 'mode_class'],
                'additionalProperties': False
            }
        }
    },
    'requiredProperties': ['modes'],
    'additionalProperties': False
}


ModeDict = dict[str, SearchToolMode]


def build_modes_from_file(path: Path) -> dict[str, SearchToolMode]:
    with open(path, 'r') as file:
        try:
            config = json.load(file)
        except json.JSONDecodeError as err:
            raise SearchToolValidationError(f'Cannot decode {path}: {err}')

        try:
            jsonschema.validate(instance=config, schema=CONFIG_SCHEMA)
        except jsonschema.exceptions.ValidationError as err:
            raise SearchToolValidationError(f'Invalid config in {path}: {err}')

    result: dict[str, SearchToolMode] = {}

    for mode_config in config['modes']:
        class_fqn = mode_config['class']
        module_name, _, class_name = class_fqn.rpartition('.')

        mode_name = mode_config['name']
        mode_param = mode_config.get('param')

        try:
            mode_class = getattr(importlib.import_module(module_name), class_name)
        except (ImportError, AttributeError):
            raise SearchToolValidationError(f'Cannot import class {class_fqn} required by mode {repr(mode_name)}')

        if not issubclass(mode_class, SearchToolMode):
            raise SearchToolValidationError(f'The class {class_fqn} required by mode {repr(mode_name)} does not satisfy the <SearchToolMode> protocol')

        try:
            jsonschema.validate(instance=mode_param, schema=mode_class.get_param_json_schema())
        except jsonschema.exceptions.ValidationError as err:
            raise SearchToolValidationError(f'Parameter validation for {repr(mode_name)} failed: {err}')

        if mode_name in result:
            raise SearchToolValidationError(f'More than one mode has name {repr(mode_name)}')

        result[mode_name] = mode_class(mode_param)

    return result
