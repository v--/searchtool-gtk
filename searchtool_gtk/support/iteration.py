import functools
from collections.abc import Callable, Iterable, Sequence


def list_accumulator[T, **P](fun: Callable[P, Iterable[T]]) -> Callable[P, Sequence[T]]:
    @functools.wraps(fun)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Sequence[T]:
        return list(fun(*args, **kwargs))

    return wrapper
