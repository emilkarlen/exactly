from typing import Generic, TypeVar, Dict, Sequence

T = TypeVar('T')


class NameAndValue(tuple, Generic[T]):
    """
    A name with an associated value.

    Is a tuple with two elements - so objects can be used wherever pairs can be used.
    """

    def __new__(cls,
                name,
                value: T):
        return tuple.__new__(cls, (name, value))

    @staticmethod
    def as_dict(elements: 'Sequence[NameAndValue[T]]') -> Dict[str, T]:
        return to_dict(elements)

    @property
    def name(self):
        return self[0]

    @property
    def value(self) -> T:
        return self[1]


def to_dict(name_and_values: Sequence[NameAndValue[T]]) -> Dict[str, T]:
    return {
        nav.name: nav.value
        for nav in name_and_values
    }
