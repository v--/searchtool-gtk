# ruff: file-ignore[non-empty-init-module]

from .app import SearchToolApp
from .styling import apply_styling


apply_styling()


__all__ = ['SearchToolApp']
