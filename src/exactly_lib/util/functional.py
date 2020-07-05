import types
from typing import TypeVar, Optional, Callable, List, Sequence

T = TypeVar('T')
U = TypeVar('U')


def compose_first_and_second(f, g):
    return Composition(g, f)


class Composition:
    def __init__(self, g, f):
        self.g = g
        self.f = f

    def __call__(self, arg):
        return self.g(self.f(arg))


def and_predicate(predicates: List[Callable[[T], bool]]) -> types.FunctionType:
    if not predicates:
        return lambda x: True
    if len(predicates) == 1:
        return predicates[0]
    return _AndPredicate(predicates)


class _AndPredicate:
    def __init__(self, predicates: List[Callable[[T], bool]]):
        self.predicates = predicates

    def __call__(self, *args, **kwargs):
        for predicate in self.predicates:
            if not predicate(*args, **kwargs):
                return False
        return True


def map_optional(f: Callable[[T], U], x: Optional[T]) -> Optional[U]:
    return (
        None
        if x is None
        else
        f(x)
    )


def reduce_optional(f: Callable[[T], U], value_if_none: U, x: Optional[T]) -> U:
    return (
        value_if_none
        if x is None
        else
        f(x)
    )


def filter_not_none(xs: Sequence[Optional[T]]) -> List[T]:
    return [
        x
        for x in xs
        if x is not None
    ]
