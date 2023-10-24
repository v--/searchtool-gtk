from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path
import importlib
import json

import jsonschema

from .exceptions import SearchToolValidationError
from .mode import SearchToolMode


CONFIG_SCHEMA = {
    'type': 'object',
    'properties': {
        'rtSignal': { 'type': 'number' },
        'name': { 'type': 'string' },
        'modeFqn': { 'type': 'string' },
        'modeParams': {}
    },
    'requiredProperties': ['rtSignal', 'name', 'mode_fqn']
}


@dataclass
class SearchToolConfigItem:
    rt_signal: int
    name: str
    mode_fqn: str
    mode_params: Any = None

    mode_class: type[SearchToolMode] = field(init=False)

    @classmethod
    def read_from_file(Cls, path: Path) -> list[SearchToolConfigItem]:
        with open(path, 'r') as file:
            try:
                objs = json.load(file)
            except json.JSONDecodeError as err:
                raise SearchToolValidationError(f'Cannot decode {path}: {err}')

            try:
                jsonschema.validate(instance=objs, schema={'type': 'array', 'items': CONFIG_SCHEMA})
            except jsonschema.exceptions.ValidationError as err:
                raise SearchToolValidationError(f'Invalid config in {path}: {err}')

            return [Cls(**obj) for obj in objs]

    def __post_init__(self):
        module_name, _, class_name = self.mode_fqn.rpartition('.')

        try:
            mode_class = getattr(importlib.import_module(module_name), class_name)
        except (ImportError, AttributeError):
            raise SearchToolValidationError(f'Cannot import mode class {self.mode_fqn}')

        if isinstance(mode_class, SearchToolMode):
            self.mode_class = mode_class
        else:
            raise SearchToolValidationError(f'Invalid mode class {self.mode_fqn}')

        jsonschema.validate(instance=self.mode_params, schema=self.mode_class.param_json_schema)
